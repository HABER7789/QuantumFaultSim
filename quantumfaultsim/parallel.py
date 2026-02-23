"""
HPC parallel sampling using Sinter.

Sinter is Google's official tool for parallelized QEC Monte Carlo sampling.
It uses Python multiprocessing — no MPI needed. Each worker gets a batch of
shots to simulate independently, then results are combined.

Verified API: sinter.collect(), sinter.Task, sinter.TaskStats
Source: https://pypi.org/project/sinter/
"""

from typing import Iterator, List

import sinter

from quantumfaultsim.circuits import CircuitConfig, build_circuit
from quantumfaultsim.config import SweepConfig
from quantumfaultsim.logger import logger


def make_tasks(config: SweepConfig) -> Iterator[sinter.Task]:
    """
    Generate all simulation tasks for a threshold sweep.

    Yields one sinter.Task per (distance, noise_rate) combination.
    json_metadata stores the parameters so we can filter results later.
    """
    for d in config.distances:
        for p in config.noise_values:
            circuit_config = CircuitConfig(
                distance=d,
                noise_model=config.noise_model,
                p=p,
            )
            circuit = build_circuit(circuit_config)

            # Extract the discrete detector error model for PyMatching (handled by sinter internally)
            yield sinter.Task(
                circuit=circuit,
                json_metadata={
                    "d": d,
                    "p": p,
                    "noise_model": config.noise_model,
                },
            )


def run_parallel_sweep(config: SweepConfig) -> List[sinter.TaskStats]:
    """
    Run Sinter Monte Carlo sampling in parallel for the provided SweepConfig.
    """
    logger.info(
        f"Starting sweep: {len(config.distances)} distances, "
        f"{len(config.noise_values)} noise rates, {config.num_workers} workers."
    )

    tasks = list(make_tasks(config))

    samples = sinter.collect(
        num_workers=config.num_workers,
        max_shots=config.max_shots,
        max_errors=config.max_errors,
        tasks=tasks,
        decoders=["pymatching"],
        print_progress=False,  # We manage logging now
        save_resume_filepath=config.save_resume_filepath,
    )

    logger.info("Parallel sweep finished collecting stats.")
    return samples


def save_samples_csv(samples: List[sinter.TaskStats], path: str) -> None:
    """Save raw sinter results to CSV for reproducibility."""
    with open(path, "w") as f:
        f.write(sinter.CSV_HEADER + "\n")
        for stat in samples:
            f.write(stat.to_csv_line() + "\n")
    print(f"Saved raw samples to {path}")
