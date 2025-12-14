"""
Graph 5: Latency Distribution

Box plot comparing response latency distributions between JSON and TOON.
"""

import matplotlib.pyplot as plt
import numpy as np

from style import COLORS, apply_style, save_figure
from common import load_results


def graph_5_latency(results=None):
    """Box plot comparing response latency distributions."""
    apply_style()

    if results is None:
        results = load_results()

    if "exp2" not in results:
        print("Skipping Graph 5: No experiment 2 results")
        return

    summary = results["exp2"]["summary"]

    json_latencies = summary["JSON"]["latencies"]
    toon_latencies = summary["TOON"]["latencies"]

    fig, ax = plt.subplots(figsize=(8, 6))

    data = [json_latencies, toon_latencies]
    positions = [1, 2]

    bp = ax.boxplot(data, positions=positions, widths=0.5, patch_artist=True)

    colors = [COLORS["JSON"], COLORS["TOON"]]
    for patch, color in zip(bp["boxes"], colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    ax.set_xticklabels(["JSON", "TOON"])
    ax.set_ylabel("Response Latency (seconds)")
    ax.set_title("Response Latency Distribution by Format", fontweight="bold")

    # Add mean annotations
    json_mean = np.mean(json_latencies)
    toon_mean = np.mean(toon_latencies)
    ax.annotate(
        f"μ = {json_mean:.2f}s",
        xy=(1, json_mean),
        xytext=(1.3, json_mean),
        fontsize=10,
        color=COLORS["JSON"],
    )
    ax.annotate(
        f"μ = {toon_mean:.2f}s",
        xy=(2, toon_mean),
        xytext=(2.3, toon_mean),
        fontsize=10,
        color=COLORS["TOON"],
    )

    improvement = ((json_mean - toon_mean) / json_mean) * 100
    ax.text(
        1.5,
        max(json_latencies) * 0.9,
        f"{improvement:.0f}% faster",
        ha="center",
        fontsize=12,
        fontweight="bold",
        color=COLORS["TOON"],
    )

    plt.tight_layout()
    save_figure(fig, "../graphics/graph_5_latency")
    plt.close()


if __name__ == "__main__":
    graph_5_latency()
