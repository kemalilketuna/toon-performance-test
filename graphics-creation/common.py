"""
Shared utilities for all graphics.
"""

import pickle
from pathlib import Path

# Output directory
OUTPUT_DIR = Path(__file__).parent


def load_results():
    """Load all experiment results."""
    results = {}

    exp1_path = OUTPUT_DIR / "exp1_results.pkl"
    if exp1_path.exists():
        with open(exp1_path, "rb") as f:
            results["exp1"] = pickle.load(f)

    exp2_path = OUTPUT_DIR / "exp2_results.pkl"
    if exp2_path.exists():
        with open(exp2_path, "rb") as f:
            results["exp2"] = pickle.load(f)

    exp3_path = OUTPUT_DIR / "exp3_results.pkl"
    if exp3_path.exists():
        with open(exp3_path, "rb") as f:
            results["exp3"] = pickle.load(f)

    return results
