"""
Graph 8: Architecture Diagram

Pipeline diagram showing where TOON fits in the stack.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from style import COLORS, apply_style, save_figure


def graph_8_architecture():
    """Pipeline diagram showing where TOON fits in the stack."""
    apply_style()

    fig, ax = plt.subplots(figsize=(14, 4))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4)
    ax.axis("off")

    # Box positions and sizes
    boxes = [
        (1, 1.5, 2, 1.5, "Database\n(SQL)", COLORS["neutral"]),
        (4, 1.5, 2, 1.5, "Backend\n(JSON)", COLORS["JSON"]),
        (7, 1.5, 2.5, 1.5, "TOON\nConverter", COLORS["TOON"]),
        (10.5, 1.5, 2, 1.5, "LLM API\n(Prompt)", COLORS["dark"]),
    ]

    for x, y, w, h, label, color in boxes:
        rect = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.05,rounding_size=0.2",
            facecolor=color,
            edgecolor="black",
            linewidth=2,
            alpha=0.8,
        )
        ax.add_patch(rect)
        ax.text(
            x + w / 2,
            y + h / 2,
            label,
            ha="center",
            va="center",
            fontsize=11,
            fontweight="bold",
            color="white" if color == COLORS["dark"] else "black",
        )

    # Arrows
    arrow_style = dict(arrowstyle="->", color="black", lw=2)
    for x1, x2 in [(3, 4), (6, 7), (9.5, 10.5)]:
        ax.annotate("", xy=(x2, 2.25), xytext=(x1, 2.25), arrowprops=arrow_style)

    # Labels under arrows
    labels = ["Query", "Data", "Optimized"]
    positions = [3.5, 6.5, 10]
    for pos, label in zip(positions, labels):
        ax.text(pos, 1.2, label, ha="center", fontsize=9, style="italic")

    ax.set_title(
        "TOON Integration: Just-In-Time Conversion Pattern",
        fontsize=14,
        fontweight="bold",
        y=1.05,
    )

    plt.tight_layout()
    save_figure(fig, "../graphics/graph_8_architecture")
    plt.close()


if __name__ == "__main__":
    graph_8_architecture()
