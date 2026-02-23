"""
Threshold estimation from Monte Carlo sweep results.

The threshold is the physical error rate where the logical error rate curves
for different code distances all cross. Below the threshold, larger d = better.
Above the threshold, larger d = worse.

Expected threshold: ~0.007 (0.7%) for circuit-level noise.
"""

import numpy as np
import sinter
from typing import List, Dict


def extract_ler_table(
    samples: List[sinter.TaskStats],
) -> Dict[int, Dict[float, tuple[float, float]]]:
    """
    Convert Sinter output to a nested dict: {distance: {p: (ler, stderr)}}.

    Statistical error (stderr) uses Wilson interval approximation.
    """
    table: Dict[int, Dict[float, tuple[float, float]]] = {}

    for stat in samples:
        if stat.shots == 0:
            continue
        d = stat.json_metadata["d"]
        p = stat.json_metadata["p"]
        ler = stat.errors / stat.shots
        # Standard error for a binomial proportion
        stderr = np.sqrt(ler * (1 - ler) / stat.shots)

        if d not in table:
            table[d] = {}
        table[d][p] = (ler, stderr)

    return table


def estimate_threshold(
    table: Dict[int, Dict[float, tuple[float, float]]],
) -> float:
    """
    Estimate threshold as the average p where LER(d_small) = LER(d_large).

    Simple linear interpolation between sampled p values.
    Expected result: ~0.007 for circuit-level depolarizing noise.
    """
    distances = sorted(table.keys())
    if len(distances) < 2:
        raise ValueError("Need at least 2 distances for threshold estimation.")

    crossing_ps = []

    for j in range(len(distances) - 1):
        d_lo = distances[j]
        d_hi = distances[j + 1]

        common_ps = sorted(set(table[d_lo].keys()) & set(table[d_hi].keys()))

        for i in range(len(common_ps) - 1):
            p1, p2 = common_ps[i], common_ps[i + 1]
            ler_lo_1, _ = table[d_lo][p1]
            ler_lo_2, _ = table[d_lo][p2]
            ler_hi_1, _ = table[d_hi][p1]
            ler_hi_2, _ = table[d_hi][p2]

            diff_1 = ler_lo_1 - ler_hi_1
            diff_2 = ler_lo_2 - ler_hi_2

            # Sign change means curves crossed between p1 and p2
            if diff_1 * diff_2 < 0:
                frac = abs(diff_1) / (abs(diff_1) + abs(diff_2))
                p_cross = p1 + frac * (p2 - p1)
                crossing_ps.append(p_cross)

    if not crossing_ps:
        return float("nan")

    return float(np.mean(crossing_ps))
