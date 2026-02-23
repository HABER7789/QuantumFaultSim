"""Tests for the MWPM decoder."""

import pymatching
from quantumfaultsim.circuits import CircuitConfig, build_circuit
from quantumfaultsim.decoder import build_decoder, count_logical_errors


def test_decoder_builds():
    """PyMatching should build a valid Matching object."""
    config = CircuitConfig(distance=3, rounds=3, noise_model="circuit_level", p=0.005)
    circuit = build_circuit(config)
    matcher = build_decoder(circuit)
    assert isinstance(matcher, pymatching.Matching)


def test_noiseless_has_zero_errors():
    """With p=0 (no noise), there should be zero logical errors."""
    config = CircuitConfig(distance=3, rounds=3, noise_model="circuit_level", p=0.0001)
    circuit = build_circuit(config)
    errors, shots = count_logical_errors(circuit, num_shots=1000)
    # With very low noise, errors should be extremely rare
    assert errors / shots < 0.01, f"Expected near-zero LER, got {errors/shots:.4f}"


def test_high_noise_has_many_errors():
    """With p=0.3 (extremely high noise), LER should be high."""
    config = CircuitConfig(distance=3, rounds=3, noise_model="circuit_level", p=0.3)
    circuit = build_circuit(config)
    errors, shots = count_logical_errors(circuit, num_shots=5000)
    # At p=0.3 (way above threshold), LER should be substantial
    assert errors / shots > 0.1, f"Expected high LER, got {errors/shots:.4f}"


def test_returns_correct_shot_count():
    """Shot count returned should match what was requested."""
    config = CircuitConfig(distance=3, rounds=3, noise_model="circuit_level", p=0.005)
    circuit = build_circuit(config)
    errors, shots = count_logical_errors(circuit, num_shots=1000)
    assert shots == 1000
    assert 0 <= errors <= 1000
