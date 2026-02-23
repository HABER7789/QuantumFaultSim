"""
Surface code circuit generation using Stim.

Verified API: stim.Circuit.generated() with "surface_code:rotated_memory_x"
Source: https://github.com/quantumlib/Stim
"""

import stim
from typing import Literal
from quantumfaultsim.config import CircuitConfig

NoiseModel = Literal["circuit_level", "phenomenological"]


def build_circuit(config: CircuitConfig) -> stim.Circuit:
    """
    Generate a rotated surface code memory experiment circuit using Stim.

    The rotated surface code is the standard choice because it uses d^2 data
    qubits instead of 2*d^2 - 1 (fewer qubits for same distance = more practical).

    Circuit-level noise: errors can occur on every gate, measurement, and reset.
    This is the most realistic noise model — used in published threshold papers.

    Returns: stim.Circuit object ready for sampling.
    """
    if config.noise_model == "circuit_level":
        return stim.Circuit.generated(
            "surface_code:rotated_memory_x",
            distance=config.distance,
            rounds=config.rounds,
            after_clifford_depolarization=config.p,
            after_reset_flip_probability=config.p,
            before_measure_flip_probability=config.p,
        )
    elif config.noise_model == "phenomenological":
        # Phenomenological: only data errors and measurement errors
        # Simpler model — threshold is ~1.0% instead of ~0.7%
        return stim.Circuit.generated(
            "surface_code:rotated_memory_x",
            distance=config.distance,
            rounds=config.rounds,
            before_round_data_depolarization=config.p,
            before_measure_flip_probability=config.p,
        )
    else:
        raise ValueError(f"Unknown noise model: {config.noise_model!r}")


def get_num_data_qubits(distance: int) -> int:
    """Returns number of data qubits for a rotated surface code of given distance."""
    return distance**2


def get_num_physical_qubits(distance: int) -> int:
    """Returns total physical qubits (data + syndrome) for a given distance."""
    return 2 * (distance**2) - 1
