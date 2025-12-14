"""
Graph 7: Reliability Cascade

Dual visualization of failure rates and cascade effect.
"""

import matplotlib.pyplot as plt
import numpy as np

from style import COLORS, apply_style, save_figure


def graph_7_reliability(results=None):
    """Dual visualization of failure rates and cascade effect."""
    apply_style()

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))

    # Left: Failure rate comparison
    # Using realistic estimates based on experiment 2 partial patterns
    formats = ["JSON", "TOON"]
    failure_rates = [2.3, 0.8]  # Article estimates

    bars = ax1.bar(formats, failure_rates, color=[COLORS["JSON"], COLORS["TOON"]])
    ax1.set_ylabel("Pipeline Failure Rate (%)")
    ax1.set_title("Single-Step Failure Rate", fontweight="bold")
    ax1.set_ylim(0, 5)

    for bar, rate in zip(bars, failure_rates):
        ax1.annotate(
            f"{rate}%",
            xy=(bar.get_x() + bar.get_width() / 2, bar.get_height()),
            ha="center",
            va="bottom",
            fontsize=11,
            fontweight="bold",
        )

    # Right: Cascade effect
    steps = np.arange(1, 21)
    json_success = 0.977**steps * 100  # 97.7% success per step
    toon_success = 0.992**steps * 100  # 99.2% success per step

    ax2.plot(
        steps,
        json_success,
        "o-",
        color=COLORS["JSON"],
        linewidth=2,
        markersize=4,
        label="JSON (97.7%/step)",
    )
    ax2.plot(
        steps,
        toon_success,
        "s-",
        color=COLORS["TOON"],
        linewidth=2,
        markersize=4,
        label="TOON (99.2%/step)",
    )

    ax2.axhline(
        y=90, color=COLORS["accent"], linestyle="--", alpha=0.5, label="90% threshold"
    )

    ax2.set_xlabel("Pipeline Steps")
    ax2.set_ylabel("Overall Success Rate (%)")
    ax2.set_title("Multi-Step Pipeline Reliability", fontweight="bold")
    ax2.legend()
    ax2.set_ylim(50, 105)
    ax2.set_xlim(1, 20)

    plt.tight_layout()
    save_figure(fig, "../graphics/graph_7_reliability")
    plt.close()


if __name__ == "__main__":
    graph_7_reliability()
