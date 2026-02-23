"""
Visualization functions. All plots saved to results/ directory.
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import sinter
from typing import List, Optional


def _ensure_images_dir() -> str:
    os.makedirs(os.path.join("docs", "images"), exist_ok=True)
    return os.path.join("docs", "images")


def plot_threshold_curve(
    samples: List[sinter.TaskStats],
    estimated_threshold: Optional[float] = None,
    filename: str = "threshold_plot.png",
) -> str:
    """
    Plot LER vs physical error rate for all code distances.

    The crossing point of all curves is the fault-tolerance threshold.
    Below threshold: curves diverge downward as d increases (QEC working).
    Above threshold: curves diverge upward as d increases (QEC failing).

    This is the MAIN result of the project — the equivalent of what appears
    in Google's Willow paper and Fowler et al. 2012.
    """
    images_dir = _ensure_images_dir()
    output_path = os.path.join(images_dir, filename)

    # Group stats by distance
    groups: dict = {}
    for stat in samples:
        if stat.shots == 0:
            continue
        d = stat.json_metadata["d"]
        p = stat.json_metadata["p"]
        ler = stat.errors / stat.shots
        stderr = np.sqrt(ler * (1 - ler) / stat.shots) if stat.shots > 0 else 0.0
        if d not in groups:
            groups[d] = {"p": [], "ler": [], "err": []}
        groups[d]["p"].append(p)
        groups[d]["ler"].append(ler)
        groups[d]["err"].append(stderr)

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = cm.plasma(np.linspace(0.1, 0.85, len(groups)))

    for (d, vals), color in zip(sorted(groups.items()), colors):
        idx = np.argsort(vals["p"])
        ps = np.array(vals["p"])[idx]
        lers = np.array(vals["ler"])[idx]
        errs = np.array(vals["err"])[idx]
        ax.errorbar(
            ps * 100,
            lers,  # multiply p by 100 to display as percentage
            yerr=errs,
            marker="o",
            label=f"d={d}",
            color=color,
            linewidth=2,
            markersize=6,
            capsize=3,
        )

    if estimated_threshold is not None and not np.isnan(estimated_threshold):
        ax.axvline(
            x=estimated_threshold * 100,
            color="black",
            linestyle="--",
            linewidth=1.5,
            label=f"Threshold ≈ {estimated_threshold*100:.2f}%",
        )

    ax.set_xlabel("Physical Error Rate (%)", fontsize=13)
    ax.set_ylabel("Logical Error Rate", fontsize=13)
    ax.set_title(
        "Rotated Surface Code Fault-Tolerance Threshold\n"
        "Circuit-Level Depolarizing Noise | MWPM Decoder (PyMatching v2)",
        fontsize=12,
    )
    ax.set_yscale("log")
    ax.legend(fontsize=11, loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")
    return output_path


def plot_ler_vs_distance(
    samples: List[sinter.TaskStats],
    target_p: float,
    filename: str = "ler_vs_distance.png",
) -> str:
    """
    At a fixed noise below threshold, show LER decreasing with d.
    This is the "money shot" — proof that QEC is actually working.
    The fundamental promise of quantum error correction visualized.
    """
    images_dir = _ensure_images_dir()
    output_path = os.path.join(images_dir, filename)

    # Find the p-value in the data closest to target_p
    available_ps = {stat.json_metadata["p"] for stat in samples if stat.shots > 0}
    if not available_ps:
        print("No valid stats for LER plot. Skipping.")
        return ""
    closest_p = min(available_ps, key=lambda x: abs(x - target_p))

    distances, lers, errs = [], [], []
    for stat in samples:
        if stat.shots == 0:
            continue
        if stat.json_metadata["p"] == closest_p:
            d = stat.json_metadata["d"]
            ler = stat.errors / stat.shots
            stderr = np.sqrt(ler * (1 - ler) / stat.shots)
            distances.append(d)
            lers.append(ler)
            errs.append(stderr)

    if not distances:
        print(f"No data found for p={closest_p}. Skipping plot.")
        return ""

    idx = np.argsort(distances)
    distances = np.array(distances)[idx]
    lers = np.array(lers)[idx]
    errs = np.array(errs)[idx]

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.errorbar(
        distances,
        lers,
        yerr=errs,
        marker="s",
        color="steelblue",
        linewidth=2,
        markersize=9,
        capsize=4,
    )
    ax.set_xlabel("Code Distance (d)", fontsize=13)
    ax.set_ylabel("Logical Error Rate", fontsize=13)
    ax.set_title(
        f"Error Suppression Below Threshold (p ≈ {closest_p*100:.2f}%)\n"
        "Larger code → Fewer logical errors → QEC is working ✓",
        fontsize=12,
    )
    ax.set_yscale("log")
    ax.set_xticks(distances)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")
    return output_path


def plot_worker_scaling(
    worker_counts: List[int],
    runtimes_seconds: List[float],
    filename: str = "scaling_benchmark.png",
) -> str:
    """
    Plot speedup vs number of workers (HPC scaling benchmark).
    Demonstrates the HPC component of the project.
    """
    images_dir = _ensure_images_dir()
    output_path = os.path.join(images_dir, filename)

    baseline = runtimes_seconds[0]
    speedups = [baseline / t for t in runtimes_seconds]
    ideal = worker_counts  # linear ideal

    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(
        worker_counts,
        speedups,
        "o-",
        color="steelblue",
        linewidth=2,
        markersize=8,
        label="Actual speedup",
    )
    ax.plot(
        worker_counts,
        ideal,
        "--",
        color="gray",
        linewidth=1.5,
        label="Ideal linear speedup",
    )
    ax.set_xlabel("Number of Workers (CPU cores)", fontsize=13)
    ax.set_ylabel("Speedup vs 1 Worker", fontsize=13)
    ax.set_title(
        "HPC Scaling: Sinter Parallel Sampling\n"
        "Monte Carlo threshold sweep (1M shots, d=3,5,7)",
        fontsize=12,
    )
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved: {output_path}")
    return output_path
