"""
Graph 4: Accuracy Comparison

Grouped bar chart comparing accuracy rates between JSON and TOON.
"""

import matplotlib.pyplot as plt
import numpy as np

from style import COLORS, apply_style, save_figure
from common import load_results


def graph_4_accuracy(results=None):
    """Grouped bar chart comparing accuracy rates."""
    apply_style()

    if results is None:
        results = load_results()

    if "exp2" not in results:
        print("Skipping Graph 4: No experiment 2 results")
        return

    summary = results["exp2"]["summary"]

    categories = ["Exact Match", "Partial Match", "Failure"]
    json_vals = [
        summary["JSON"]["exact_rate"],
        summary["JSON"]["partial_rate"],
        summary["JSON"]["failure_rate"],
    ]
    toon_vals = [
        summary["TOON"]["exact_rate"],
        summary["TOON"]["partial_rate"],
        summary["TOON"]["failure_rate"],
    ]

    x = np.arange(len(categories))
    width = 0.35

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar(x - width / 2, json_vals, width, label="JSON", color=COLORS["JSON"])
    bars2 = ax.bar(x + width / 2, toon_vals, width, label="TOON", color=COLORS["TOON"])

    ax.set_ylabel("Percentage (%)")
    ax.set_title("LLM Comprehension Accuracy: JSON vs TOON", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(categories)
    ax.legend()
    ax.set_ylim(0, 100)

    # Add value labels
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height:.1f}%",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                ha="center",
                va="bottom",
                fontsize=9,
            )

    plt.tight_layout()
    save_figure(fig, "../graphics/graph_4_accuracy")
    plt.close()


if __name__ == "__main__":
    graph_4_accuracy()
