"""
Command-line interface using Click.
Usage: python -m quantumfaultsim.cli [COMMAND] [OPTIONS]
"""

import click
import os
import sys
from pydantic import ValidationError
from quantumfaultsim.sampler import run_single_point
from quantumfaultsim.parallel import run_parallel_sweep, save_samples_csv
from quantumfaultsim.config import SweepConfig
from quantumfaultsim.logger import setup_logger
from .threshold import extract_ler_table, estimate_threshold
from .plots import plot_threshold_curve, plot_ler_vs_distance


@click.group(help="""
QuantumFaultSim: High-Performance Surface Code Threshold Simulator.

This CLI provides tools to run Quantum Error Correction (QEC) simulations
using Stim and PyMatching. You can run single points or full HPC sweeps.
""")
@click.option(
    "--log-level",
    default="INFO",
    type=click.Choice(["DEBUG", "INFO", "WARNING"]),
    help="Set the logging level for debug tracking.",
)
def cli(log_level):
    """QuantumFaultSim: Surface Code Threshold Simulator"""
    setup_logger(level=log_level)


@cli.command(help="""
Run a single Monte Carlo simulation point to verify logical error rate.

Good for quick testing of a specific code distance and physical error rate 
combination without waiting for a full multiprocessor sweep.
""")
@click.option(
    "--distance",
    "-d",
    default=5,
    show_default=True,
    help="Surface code distance (odd integer: 3, 5, 7, 9, 11). Higher is more protective.",
)
@click.option(
    "--noise",
    "-p",
    default=0.005,
    show_default=True,
    help="Physical error rate for the gate noise (e.g. 0.003 = 0.3%).",
)
@click.option(
    "--shots",
    "-s",
    default=100_000,
    show_default=True,
    help="Number of Monte Carlo shots to execute.",
)
@click.option(
    "--model",
    "-m",
    default="circuit_level",
    show_default=True,
    type=click.Choice(["circuit_level", "phenomenological"]),
    help="Type of noise model (circuit_level injects noise on every fundamental gate).",
)
@click.option(
    "--seed", type=int, default=None, help="Random seed for perfect reproducibility."
)
@click.option(
    "--out", "-o", default=None, help="Save the result statistics to a JSON file path."
)
def simulate(distance, noise, shots, model, seed, out):
    click.echo("\nSimulating surface code:")
    click.echo(f"  Distance     : d={distance} ({distance**2} data qubits)")
    click.echo(f"  Noise rate   : p={noise:.4f} ({noise*100:.2f}%)")
    click.echo(f"  Shots        : {shots:,}")
    click.echo(f"  Noise model  : {model}")
    click.echo("")

    try:
        result = run_single_point(
            distance=distance, p=noise, num_shots=shots, noise_model=model, seed=seed
        )
    except ValidationError as e:
        click.echo(f"\n[ERROR] Invalid configuration parameters:\n{e}")
        sys.exit(1)
    except ValueError as e:
        click.echo(f"\n[ERROR] {e}")
        sys.exit(1)

    click.echo("RESULT:")
    click.echo(
        f"  Logical Error Rate : {result.logical_error_rate:.6f} "
        f"({result.logical_error_rate*100:.4f}%)"
    )
    click.echo(f"  Logical Errors     : {result.num_errors:,} / {result.num_shots:,}")
    click.echo(f"  Runtime            : {result.runtime_seconds:.1f}s")

    # Interpretation
    if result.logical_error_rate < noise:
        click.echo(
            f"\n  [PASS] LER ({result.logical_error_rate:.4f}) < p ({noise:.4f})"
        )
        click.echo("         ERROR SUPPRESSION — operating below threshold")
    else:
        click.echo(
            f"\n  [FAIL] LER ({result.logical_error_rate:.4f}) > p ({noise:.4f})"
        )
        click.echo("         ERROR AMPLIFICATION — operating above threshold")

    if out:
        result.to_json(out)


@cli.command(help="""
Run a full threshold sweep over multiple distances and physical error rates.

Automatically spans a grid of parameters, distributes the Monte Carlo sampling
across CPU workers using Sinter, and generates the resulting threshold 
and scaling plots in the `results/` directory.

Sinter adaptively manages workloads: point sampling stops automatically when either 
`max-shots` OR `max-errors` is reached, saving significant compute time.
""")
@click.option(
    "--distances",
    type=str,
    default="3,5,7,9,11",
    help="Comma-separated list of code distances. Provide at least two for threshold estimation.",
)
@click.option(
    "--p-start",
    type=float,
    default=0.001,
    help="Starting physical error rate (e.g. 0.001).",
)
@click.option(
    "--p-end",
    type=float,
    default=0.015,
    help="Ending physical error rate (e.g. 0.015).",
)
@click.option(
    "--p-steps",
    type=int,
    default=8,
    help="Number of interpolated steps between p-start and p-end.",
)
@click.option(
    "--noise-model",
    default="circuit_level",
    show_default=True,
    type=click.Choice(["circuit_level", "phenomenological"]),
    help="Mathematical noise model to inject into the quantum circuit.",
)
@click.option(
    "--workers", type=int, default=4, help="Number of parallel CPU cores to utilize."
)
@click.option(
    "--max-shots",
    type=int,
    default=500_000,
    help="Hard maximum limit of Monte Carlo shots per data point.",
)
@click.option(
    "--max-errors",
    type=int,
    default=500,
    help="Adaptive target: stop collecting a data point once this many logical errors are found to save time.",
)
@click.option(
    "--resume",
    type=click.Path(),
    default=None,
    help="Path to a CSV file to save/resume progress. Resuming from this file skips already-completed data points.",
)
def sweep(
    distances,
    p_start,
    p_end,
    p_steps,
    noise_model,
    workers,
    max_shots,
    max_errors,
    resume,
):
    import numpy as np
    import time

    dist_list = [int(d) for d in distances.split(",")]
    noise_values = list(np.linspace(p_start, p_end, p_steps))

    click.echo("\nThreshold sweep:")
    click.echo(f"  Distances  : {dist_list}")
    click.echo(f"  Noise rates: {noise_values}")
    click.echo(f"  Noise model: {noise_model}")
    click.echo(f"  Workers    : {workers}")
    click.echo(f"  Max shots  : {max_shots:,} per point")
    click.echo(f"  Max errors : {max_errors:,} per point")
    click.echo(f"  Tasks      : {len(dist_list) * len(noise_values)}")
    if resume:
        click.echo(f"  Resume file: {resume}")
    click.echo("")

    try:
        config = SweepConfig(
            distances=dist_list,
            noise_values=noise_values,
            noise_model=noise_model,
            num_workers=workers,
            max_shots=max_shots,
            max_errors=max_errors,
            save_resume_filepath=resume,
        )
    except ValidationError as e:
        click.echo(f"\n[ERROR] Invalid sweep configuration:\n{e}")
        sys.exit(1)
    except ValueError as e:
        click.echo(f"\n[ERROR] {e}")
        sys.exit(1)

    t0 = time.time()
    # Run the sweep
    samples = run_parallel_sweep(config)

    if resume:
        save_samples_csv(samples, resume)

    elapsed = time.time() - t0
    click.echo(f"\nCompleted in {elapsed:.0f}s ({elapsed/60:.1f} min)")

    os.makedirs("results", exist_ok=True)
    save_samples_csv(samples, "results/raw_samples.csv")

    table = extract_ler_table(samples)
    threshold = estimate_threshold(table)
    click.echo(f"\nEstimated threshold: p_th ≈ {threshold:.4f} ({threshold*100:.2f}%)")
    click.echo("Expected:            p_th ≈ 0.0070 (0.70%) for circuit-level noise")

    plot_threshold_curve(samples, estimated_threshold=threshold)
    plot_ler_vs_distance(samples, target_p=0.003)
    click.echo("\nPlots saved to docs/images/")


if __name__ == "__main__":
    cli()
