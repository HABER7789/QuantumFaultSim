# Current Status

**Status: Functional / Baseline Complete**

All core modules have been fully implemented, wrapped with CLI commands, and functionally verified.

## Completed Modules
- `circuits.py`: Generates rotated surface code circuits with `phenomenological` and `circuit_level` noise models.
- `decoder.py`: Correctly extracts Detector Error Models (DEM) and decodes syndromes using MWPM via PyMatching.
- `sampler.py`: Single-process Monte Carlo validation script.
- `parallel.py`: Fully functional wrapper around Sinter for executing multi-core threshold sweeps. 
    - *Note:* Implementing parallel processing immediately revealed a `multiprocessing` spawn issue inherent to macOS. This was permanently fixed by properly gating script execution behind `if __name__ == '__main__':` safeguards.
- `threshold.py` / `plots.py`: Properly collects raw Sinter task stats, establishes empirical threshold interpolations, and pushes cleanly formatted `matplotlib` figures to the `results/` folder.

## Verification
- Phase 1 checks passed: Sanity tests correctly demonstrated error suppression below threshold and error amplification above it.
- Phase 2/3 checks passed: Parallel sweeps generate CSV tracking files and accurate visualization charts. 
- A benchmark sweep (up to $d=11$) was completed successfully predicting a threshold of ~$0.75\%$ within a short timescale.
