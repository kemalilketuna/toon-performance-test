"""
Graph 1: Token Breakdown Diagram

Side-by-side visualization showing token structure differences between JSON and TOON.
"""

import matplotlib.pyplot as plt

from style import COLORS, apply_style, save_figure


def graph_1_token_breakdown():
    """Side-by-side visualization showing token structure differences with modern design."""
    apply_style()

    fig, axes = plt.subplots(1, 2, figsize=(14, 8))
    fig.patch.set_facecolor("white")

    # JSON example with token highlights
    json_lines = [
        ('{ "users": [', "structure"),
        ('  { "id": 1, "name": "Alice", "role": "admin" },', "data"),
        ('  { "id": 2, "name": "Bob", "role": "user" },', "data"),
        ('  { "id": 3, "name": "Charlie", "role": "user" }', "data"),
        ("] }", "structure"),
    ]

    # TOON example
    toon_lines = [
        ("users[3]{id,name,role}:", "header"),
        ("1,Alice,admin", "data"),
        ("2,Bob,user", "data"),
        ("3,Charlie,user", "data"),
    ]

    # Plot JSON
    ax1 = axes[0]
    ax1.set_xlim(-0.5, 12)
    ax1.set_ylim(-0.5, len(json_lines) + 2)
    ax1.set_title("JSON Format (~150 tokens)", fontsize=18, fontweight="bold", pad=20)
    ax1.axis("off")

    for i, (line, line_type) in enumerate(reversed(json_lines)):
        y = i + 0.8
        if line_type == "structure":
            facecolor = "#f8f9fa"
            edgecolor = COLORS["neutral"]
            linewidth = 1.5
        else:
            facecolor = "white"
            edgecolor = COLORS["accent"]
            linewidth = 2.5

        ax1.text(
            0.3,
            y,
            line,
            fontfamily="monospace",
            fontsize=12,
            verticalalignment="center",
            bbox=dict(
                boxstyle="round,pad=0.4,rounding_size=0.15",
                facecolor=facecolor,
                edgecolor=edgecolor,
                linewidth=linewidth,
            ),
        )

    # Add annotation for repeated keys with arrow
    ax1.annotate(
        "Keys repeated\n3× each",
        xy=(9.5, 2.5),
        fontsize=12,
        ha="center",
        color=COLORS["accent"],
        fontweight="bold",
    )

    # Plot TOON
    ax2 = axes[1]
    ax2.set_xlim(-0.5, 12)
    ax2.set_ylim(-0.5, len(toon_lines) + 2)
    ax2.set_title("TOON Format (~90 tokens)", fontsize=18, fontweight="bold", pad=20)
    ax2.axis("off")

    for i, (line, line_type) in enumerate(reversed(toon_lines)):
        y = i + 0.8
        if line_type == "header":
            facecolor = COLORS["TOON"]
            edgecolor = "#27ae60"
            textcolor = "white"
            linewidth = 2.5
        else:
            facecolor = "#f8f9fa"
            edgecolor = COLORS["dark"]
            textcolor = "black"
            linewidth = 1.5

        ax2.text(
            0.3,
            y,
            line,
            fontfamily="monospace",
            fontsize=12,
            verticalalignment="center",
            color=textcolor,
            bbox=dict(
                boxstyle="round,pad=0.4,rounding_size=0.15",
                facecolor=facecolor,
                edgecolor=edgecolor,
                linewidth=linewidth,
            ),
        )

    # Add annotation for single header
    ax2.annotate(
        "Keys declared\nonce in header",
        xy=(9.5, 3.5),
        fontsize=12,
        ha="center",
        color=COLORS["TOON"],
        fontweight="bold",
    )

    plt.tight_layout(pad=2)
    save_figure(fig, "../graphics/graph_1_token_breakdown")
    plt.close()


if __name__ == "__main__":
    graph_1_token_breakdown()
