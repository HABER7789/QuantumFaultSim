# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-02-20
### Added
- **Production Grade Release**
- Formal CLI entry points (`quantumfaultsim sweep`).
- Pydantic-backed `config.py` strict input validation.
- Checkpoint saving & resuming for Sinter HPC sweeps (`--resume` flag).
- `logger.py` structured INFO/DEBUG tracking.
- Automated CI pipeline with GitHub Actions and `pytest`.
- Phase 1 sanity check fixes to respect physical models at $d=3$.

## [0.1.0] - 2026-02-18
### Added
- Initial Baseline.
- `circuits.py`: Stim code generation.
- `decoder.py`: PyMatching MWPM graphs.
- Proof of $0.7\%$ threshold extraction logic via Python scripts.
