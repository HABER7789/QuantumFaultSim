import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict


def setup_logger(name: str = "quantumfaultsim", level: str = "INFO") -> logging.Logger:
    """Sets up a structured logger for the project."""
    logger = logging.getLogger(name)

    # Avoid adding multiple handlers if setup is called multiple times
    if logger.hasHandlers():
        logger.setLevel(level)
        return logger

    logger.setLevel(level)

    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)-8s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def save_metadata(
    config: Dict[str, Any], results_dir: str | Path, filename: str = "config.json"
) -> None:
    """Saves the sweep configuration metadata to the results directory."""
    out_path = Path(results_dir) / filename
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(config, f, indent=4)


logger = setup_logger()
