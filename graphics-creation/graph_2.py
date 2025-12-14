"""
Graph 2: Token Counts Bar Chart

Bar chart comparing token counts across formats and dataset sizes.
"""

import matplotlib.pyplot as plt
import numpy as np

from style import COLORS, apply_style, save_figure
from common import load_results


def graph_2_token_counts(results=None):
    """Bar chart comparing token counts across formats and dataset sizes."""
    apply_style()

    if results is None:
        results = load_results()

    if "exp1" not in results:
        print("Skipping Graph 2: No experiment 1 results")
        return

    data = results["exp1"]
    records = [d["records"] for d in data]
    json_tokens = [d["json_tokens"] for d in data]
    yaml_tokens = [d["yaml_tokens"] for d in data]
    toon_tokens = [d["toon_tokens"] for d in data]

    x = np.arange(len(records))
    width = 0.25

    fig, ax = plt.subplots(figsize=(10, 6))

    bars1 = ax.bar(x - width, json_tokens, width, label="JSON", color=COLORS["JSON"])
    bars2 = ax.bar(x, yaml_tokens, width, label="YAML", color=COLORS["YAML"])
    bars3 = ax.bar(x + width, toon_tokens, width, label="TOON", color=COLORS["TOON"])

    ax.set_xlabel("Number of Records")
    ax.set_ylabel("Token Count")
    ax.set_title("Token Consumption by Format and Dataset Size", fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(records)
    ax.legend()

    # Add savings annotations on TOON bars
    for i, (bar, d) in enumerate(zip(bars3, data)):
        savings = d["toon_savings"]
        ax.annotate(
            f"-{savings:.0f}%",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
            fontsize=9,
            color=COLORS["TOON"],
            fontweight="bold",
        )

    ax.set_ylim(0, max(json_tokens) * 1.15)

    plt.tight_layout()
    save_figure(fig, "../graphics/graph_2_token_counts")
    plt.close()


if __name__ == "__main__":
    graph_2_token_counts()
