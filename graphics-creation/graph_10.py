"""
Graph 10: Summary Infographic

Three-perspective summary with key metrics - larger readable text.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from style import COLORS, apply_style, save_figure
from common import load_results


def graph_10_summary(results=None):
    """Three-perspective summary with key metrics - larger readable text."""
    apply_style()

    if results is None:
        results = load_results()

    fig, ax = plt.subplots(figsize=(14, 10))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title
    ax.text(
        7,
        9.5,
        "TOON: Token-Oriented Object Notation",
        ha="center",
        fontsize=24,
        fontweight="bold",
    )
    ax.text(
        7,
        8.9,
        "Key Benefits Across Perspectives",
        ha="center",
        fontsize=16,
        style="italic",
        color=COLORS["neutral"],
    )

    # Get actual savings from results
    if "exp1" in results:
        token_savings = results["exp1"][-1]["toon_savings"]
    else:
        token_savings = 67

    # Central metrics - larger circles and text
    metrics = [
        (f"{token_savings:.0f}%", "Token\nSavings"),
        ("3×", "Reliability\nImprovement"),
        ("Zero", "Migration\nRequired"),
    ]

    for i, (value, label) in enumerate(metrics):
        x = 2.5 + i * 4.5

        # Larger circle for metric
        circle = plt.Circle(
            (x, 6),
            1.3,
            facecolor=COLORS["TOON"],
            edgecolor="#27ae60",
            linewidth=3,
            alpha=0.9,
        )
        ax.add_patch(circle)
        ax.text(
            x,
            6.3,
            value,
            ha="center",
            va="center",
            fontsize=28,
            fontweight="bold",
            color="white",
        )
        ax.text(
            x,
            5.5,
            label,
            ha="center",
            va="center",
            fontsize=12,
            color="white",
            linespacing=1.3,
        )

    # Three perspectives at bottom - larger boxes and text
    perspectives = [
        (
            "AI Engineer",
            "Cost reduction\nMore context capacity\nFaster inference",
            COLORS["JSON"],
        ),
        (
            "Agent Developer",
            "Reliable parsing\nFail-fast validation\nStreaming support",
            COLORS["YAML"],
        ),
        (
            "Software Developer",
            "Drop-in middleware\nNo upstream changes\nReversible adoption",
            COLORS["TOON"],
        ),
    ]

    for i, (title, benefits, color) in enumerate(perspectives):
        x = 2.5 + i * 4.5

        # Larger box
        rect = FancyBboxPatch(
            (x - 2, 0.5),
            4,
            3.3,
            boxstyle="round,pad=0.05,rounding_size=0.15",
            facecolor=color,
            edgecolor="black",
            linewidth=2,
            alpha=0.3,
        )
        ax.add_patch(rect)

        ax.text(x, 3.4, title, ha="center", va="center", fontsize=16, fontweight="bold")
        ax.text(
            x, 1.9, benefits, ha="center", va="center", fontsize=13, linespacing=1.6
        )

    plt.tight_layout(pad=1.5)
    save_figure(fig, "../graphics/graph_10_summary")
    plt.close()


if __name__ == "__main__":
    graph_10_summary()
