# Quickstart Guide

Getting started with the QuantumFaultSim threshold simulator.

## 1. Installation

This project requires **Python 3.10+**. Clone the repository and install it in editable mode:

```bash
git clone https://github.com/your-username/QuantumFaultSim.git
cd QuantumFaultSim

# Create a clean virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the package and dependencies
pip install -e .
```

## 2. Verify Installation

Run the basic validation script:
```bash
python scripts/run_phase1_verify.py
```
*Expected Output:* Logical error rate decays as code distance increases when operating below threshold.

## 3. Run a Sweep

Run a parallel threshold sweep across local CPU cores:
```bash
quantumfaultsim sweep \
    --distances 3,5,7 \
    --p-start 0.001 --p-end 0.015 --p-steps 8 \
    --workers 4 \
    --max-shots 100000 \
    --resume results/quick_checkpoint.csv
```

## 4. Output Data
All data is saved to the `results/` directory:
- `results/raw_samples.csv`: Raw sample statistics and LER data.
- `results/config.json`: Run configuration metadata.
- `results/threshold_plot.png`: Threshold crossing plot.
- `results/ler_vs_distance.png`: Error suppression plot.

*Note: Sinter adaptively targets errors. If the `sweep` command is interrupted, rerunning it with the same `--resume` file will continue from the last completed point.*
