"""
Phase 2/3 main script: Full threshold sweep with HPC parallel sampling.
Expected runtime: 5-20 minutes depending on your Mac's CPU count.
Expected result: threshold at ~0.007 (0.7%)
"""

import sys
import os
import time

sys.path.insert(0, ".")

from quantumfaultsim.parallel import run_parallel_sweep, save_samples_csv
from quantumfaultsim.threshold import extract_ler_table, estimate_threshold
from quantumfaultsim.plots import plot_threshold_curve, plot_ler_vs_distance
from quantumfaultsim.config import SweepConfig
from quantumfaultsim.logger import logger, save_metadata


def main():
    os.makedirs("results", exist_ok=True)

    # ── Strict Configuration ───────────────────────────────────────
    config = SweepConfig(
        distances=[3, 5, 7, 9, 11],
        noise_values=[0.001, 0.003, 0.005, 0.007, 0.009, 0.011, 0.013, 0.015],
        num_workers=4,
        max_shots=50_000,
        max_errors=100,
        save_resume_filepath="results/sweep_checkpoint.csv",
    )
    # ───────────────────────────────────────────────────────────────

    logger.info("Initializing HPC threshold sweep.")
    t0 = time.time()

    samples = run_parallel_sweep(config)

    elapsed = time.time() - t0
    logger.info(f"Finished simulation in {elapsed:.0f}s ({elapsed/60:.1f} min)")

    # Save outputs and metadata
    save_samples_csv(samples, "results/raw_samples.csv")
    save_metadata(config.model_dump(), "results/")

    # Estimate threshold
    table = extract_ler_table(samples)
    threshold = estimate_threshold(table)
    logger.info(f"Estimated threshold : p_th = {threshold:.4f} ({threshold*100:.2f}%)")

    # Generate plots
    plot_threshold_curve(samples, estimated_threshold=threshold)
    plot_ler_vs_distance(samples, target_p=0.003)

    print("\nAll results saved to results/")
    print("Copy results/threshold_plot.png to docs/images/ for README")


if __name__ == "__main__":
    main()
