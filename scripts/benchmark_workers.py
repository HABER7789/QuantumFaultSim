"""
Phase 3 HPC benchmark: measure speedup as worker count increases.
This is the 'scaling plot' for the LinkedIn post and README.
Tests with a small sweep (d=3,5,7, p=0.003,0.007,0.011) for speed.
"""

import sys
import os
import time

sys.path.insert(0, ".")

from quantumfaultsim.parallel import run_parallel_sweep
from quantumfaultsim.plots import plot_worker_scaling
from quantumfaultsim.config import SweepConfig


def main():
    # Small but representative sweep for benchmarking
    DISTANCES = [3, 5, 7]
    NOISE_VALUES = [0.003, 0.007, 0.011]
    MAX_SHOTS = 30_000
    MAX_ERRORS = 100

    # Import multiprocessing to detect core count
    import multiprocessing

    max_cores = multiprocessing.cpu_count()
    print(f"Your Mac has {max_cores} CPU cores")

    # Test with increasing worker counts
    worker_counts = [1, 2, 4]
    if max_cores >= 8:
        worker_counts.append(8)

    runtimes = []

    for w in worker_counts:
        print(f"\nTesting {w} workers...")
        t0 = time.time()
        config = SweepConfig(
            distances=DISTANCES,
            noise_values=NOISE_VALUES,
            num_workers=w,
            max_shots=MAX_SHOTS,
            max_errors=MAX_ERRORS,
            noise_model="circuit_level",
        )
        run_parallel_sweep(config)
        elapsed = time.time() - t0
        runtimes.append(elapsed)
        print(f"  {w} workers: {elapsed:.1f}s")

    print("\nScaling results:")
    baseline = runtimes[0]
    for w, t in zip(worker_counts, runtimes):
        speedup = baseline / t
        efficiency = speedup / w * 100
        print(
            f"  {w:2d} workers: {t:.1f}s | speedup={speedup:.2f}x | efficiency={efficiency:.0f}%"
        )

    os.makedirs("results", exist_ok=True)
    plot_worker_scaling(worker_counts, runtimes)
    print("\nSaved: results/scaling_benchmark.png")


if __name__ == "__main__":
    main()
