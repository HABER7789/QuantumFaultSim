"""
Single-process Monte Carlo sampler.
Use this for Phase 1 testing and small simulations.
For large sweeps (Phase 2+), use parallel.py with Sinter.
"""

import time
import json
from dataclasses import dataclass, asdict
from .circuits import CircuitConfig, build_circuit
from .decoder import count_logical_errors


@dataclass
class SampleResult:
    """Result of a single (distance, p) simulation point."""

    distance: int
    rounds: int
    noise_model: str
    noise_p: float
    num_shots: int
    num_errors: int
    logical_error_rate: float
    runtime_seconds: float

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(asdict(self), f, indent=2)
        print(f"Saved result to {path}")


def run_single_point(
    distance: int,
    p: float,
    num_shots: int = 100_000,
    noise_model: str = "circuit_level",
    seed: int = None,
) -> SampleResult:
    """
    Simulate one (distance, noise_rate) point.

    Args:
        distance:   Code distance (3, 5, 7, 9, 11)
        p:          Physical error rate (e.g. 0.003, 0.007, 0.012)
        num_shots:  Number of Monte Carlo samples (more = more accurate)
        noise_model: "circuit_level" or "phenomenological"
        seed:       Optional integer for reproducible random sampling

    Returns: SampleResult with logical error rate and timing.
    """
    config = CircuitConfig(
        distance=distance,
        rounds=distance,
        noise_model=noise_model,
        p=p,
    )
    circuit = build_circuit(config)

    t0 = time.time()
    errors, shots = count_logical_errors(circuit, num_shots, seed=seed)
    elapsed = time.time() - t0

    return SampleResult(
        distance=distance,
        rounds=distance,
        noise_model=noise_model,
        noise_p=p,
        num_shots=shots,
        num_errors=errors,
        logical_error_rate=errors / shots,
        runtime_seconds=elapsed,
    )
