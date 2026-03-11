"""
MWPM decoder wrapper using PyMatching v2.

Minimum Weight Perfect Matching (MWPM): when errors occur, they leave "detection
events" (syndromes). MWPM finds the most probable set of errors that explains
the observed syndromes — like solving a puzzle of which errors most likely happened.

Verified API: pymatching.Matching.from_detector_error_model()
Source: https://pymatching.readthedocs.io
"""

import math
import stim
import pymatching
import numpy as np


def build_decoder(
    circuit: stim.Circuit, use_custom_weights: bool = True
) -> pymatching.Matching:
    """
    Build a MWPM decoder from a Stim circuit.

    Steps:
    1. Extract the Detector Error Model (DEM) from the circuit.
       The DEM is a graph where nodes = detectors, edges = error mechanisms.
    2. decompose_errors=True: ensures all errors are "graphlike"
       (each error causes exactly 1 or 2 detection events — required for MWPM).
    3. If use_custom_weights=True, we manually parse Stim's DEM and
       construct the PyMatching graph from scratch to demonstrate first-principles
       understanding of edge weight calculations: weight = ln((1-p)/p).
       Otherwise, use the optimized C++ backend.

    Returns: pymatching.Matching object ready to decode syndromes.
    """
    dem = circuit.detector_error_model(decompose_errors=True)

    if not use_custom_weights:
        return pymatching.Matching.from_detector_error_model(dem)

    matcher = pymatching.Matching()

    for instruction in dem:
        if instruction.type == "error":
            p = instruction.args_copy()[0]
            if p <= 0 or p >= 1:
                continue

            # Calculate the explicit MWPM edge weight
            weight = math.log((1 - p) / p)

            # Extract nodes (detectors) and observables (faults)
            targets = instruction.targets_copy()
            detectors = [t.val for t in targets if t.is_relative_detector_id()]
            observables = [t.val for t in targets if t.is_logical_observable_id()]

            if len(detectors) == 2:
                matcher.add_edge(
                    detectors[0],
                    detectors[1],
                    weight=weight,
                    fault_ids=set(observables),
                    error_probability=p,
                    merge_strategy="independent",
                )
            elif len(detectors) == 1:
                matcher.add_boundary_edge(
                    detectors[0],
                    weight=weight,
                    fault_ids=set(observables),
                    error_probability=p,
                    merge_strategy="independent",
                )

    return matcher


def count_logical_errors(
    circuit: stim.Circuit,
    num_shots: int,
    seed: int = None,
) -> tuple[int, int]:
    """
    Run Monte Carlo simulation and count logical errors.

    For each shot:
    1. Stim simulates the noisy circuit and outputs detector measurements (syndromes)
    2. PyMatching decodes: given the syndromes, what errors most likely occurred?
    3. Compare predicted observable flips vs actual: mismatch = logical error

    Returns: (num_logical_errors, num_shots)
    Logical Error Rate = num_logical_errors / num_shots
    """
    matcher = build_decoder(circuit)
    sampler = circuit.compile_detector_sampler(seed=seed)

    detection_events, observable_flips = sampler.sample(
        shots=num_shots,
        separate_observables=True,
    )

    # decode_batch is faster than looping over decode() — iterates in C++
    predictions = matcher.decode_batch(detection_events)

    # A logical error occurs when prediction disagrees with actual observable
    num_errors = int(np.sum(np.any(predictions != observable_flips, axis=1)))

    return num_errors, num_shots
