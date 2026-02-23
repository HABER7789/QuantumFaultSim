"""Tests for circuit generation. All tests use real Stim circuits."""

import pytest
import stim
from quantumfaultsim.circuits import (
    CircuitConfig,
    build_circuit,
    get_num_data_qubits,
)


def test_circuit_builds_without_error():
    """Stim should build the circuit with no exceptions."""
    config = CircuitConfig(distance=3, rounds=3, noise_model="circuit_level", p=0.005)
    circuit = build_circuit(config)
    assert isinstance(circuit, stim.Circuit)


def test_circuit_has_detectors():
    """Surface code circuit must have detectors for decoding to work."""
    config = CircuitConfig(distance=3, rounds=3, noise_model="circuit_level", p=0.005)
    circuit = build_circuit(config)
    # A d=3, rounds=3 circuit should have detectors
    assert circuit.num_detectors > 0


def test_circuit_has_observables():
    """Must have at least 1 logical observable to measure logical errors."""
    config = CircuitConfig(distance=5, rounds=5, noise_model="circuit_level", p=0.005)
    circuit = build_circuit(config)
    assert circuit.num_observables >= 1


@pytest.mark.parametrize("d, expected_qubits", [(3, 9), (5, 25), (7, 49), (9, 81)])
def test_data_qubit_count(d, expected_qubits):
    assert get_num_data_qubits(d) == expected_qubits


def test_even_distance_raises():
    with pytest.raises(ValueError, match="odd"):
        CircuitConfig(distance=4, rounds=4, noise_model="circuit_level", p=0.005)


def test_invalid_noise_raises():
    with pytest.raises(ValueError):
        CircuitConfig(distance=3, rounds=3, noise_model="circuit_level", p=1.5)


def test_phenomenological_circuit_builds():
    config = CircuitConfig(distance=3, rounds=3, noise_model="phenomenological", p=0.01)
    circuit = build_circuit(config)
    assert isinstance(circuit, stim.Circuit)
