"""
Graph 9: Decision Flowchart

Flowchart for format selection - horizontal layout with large text.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from style import COLORS, apply_style, save_figure


def graph_9_decision_flowchart():
    """Flowchart for format selection - horizontal layout with large text."""
    apply_style()

    fig, ax = plt.subplots(figsize=(20, 10))
    fig.patch.set_facecolor("white")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 10)
    ax.axis("off")

    # Title at top
    ax.text(
        10,
        9.3,
        "Format Selection Decision Tree",
        ha="center",
        fontsize=28,
        fontweight="bold",
    )

    # Horizontal layout positions (left to right flow)
    start_x, start_y = 2, 5
    d1_x, d1_y = 6, 5
    json_x, json_y = 6, 8.2
    d2_x, d2_y = 11, 5
    yaml1_x, yaml1_y = 11, 1.5
    d3_x, d3_y = 16, 5
    yaml2_x, yaml2_y = 16, 8.2
    toon_x, toon_y = 19, 5

    def draw_start_box(x, y, text):
        """Draw the start box."""
        w, h = 3.4, 1.4
        rect = FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.03,rounding_size=0.2",
            facecolor=COLORS["dark"],
            edgecolor=COLORS["dark"],
            linewidth=3,
        )
        ax.add_patch(rect)
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=16,
            fontweight="bold",
            color="white",
        )

    def draw_diamond(x, y, text):
        """Draw a decision diamond."""
        w, h = 1.8, 1.5
        diamond = plt.Polygon(
            [(x - w, y), (x, y + h), (x + w, y), (x, y - h)],
            facecolor="#bdc3c7",
            edgecolor="#7f8c8d",
            linewidth=2.5,
            alpha=0.9,
        )
        ax.add_patch(diamond)
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=15,
            fontweight="bold",
            wrap=True,
        )

    def draw_result_box(x, y, text, color):
        """Draw a result box."""
        w, h = 2.6, 1.1
        rect = FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle="round,pad=0.03,rounding_size=0.2",
            facecolor=color,
            edgecolor="black" if color != COLORS["TOON"] else "#27ae60",
            linewidth=3,
        )
        ax.add_patch(rect)
        textcolor = "white" if color == COLORS["TOON"] else "black"
        ax.text(
            x,
            y,
            text,
            ha="center",
            va="center",
            fontsize=18,
            fontweight="bold",
            color=textcolor,
        )

    def draw_arrow(x1, y1, x2, y2, label="", label_offset=(0, 0.35)):
        """Draw an arrow with optional label."""
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops=dict(
                arrowstyle="-|>",
                color="black",
                lw=2.5,
                mutation_scale=20,
            ),
        )
        if label:
            mid_x = (x1 + x2) / 2 + label_offset[0]
            mid_y = (y1 + y2) / 2 + label_offset[1]
            ax.text(mid_x, mid_y, label, fontsize=15, style="italic", fontweight="bold")

    # Draw elements
    draw_start_box(start_x, start_y, "Start:\nData to serialize")

    draw_diamond(d1_x, d1_y, "LLM input\nor output?")
    draw_result_box(json_x, json_y, "Use JSON", COLORS["JSON"])

    draw_diamond(d2_x, d2_y, "Is data\ntabular?")
    draw_result_box(yaml1_x, yaml1_y, "Use YAML", COLORS["YAML"])

    draw_diamond(d3_x, d3_y, "Uniform\nschema?")
    draw_result_box(yaml2_x, yaml2_y, "Use YAML", COLORS["YAML"])

    draw_result_box(toon_x, toon_y, "Use TOON", COLORS["TOON"])

    # Draw arrows (horizontal flow)
    # Start -> D1
    draw_arrow(start_x + 1.7, start_y, d1_x - 1.8, d1_y)
    # D1 -> JSON (up, Output)
    draw_arrow(d1_x, d1_y + 1.5, json_x, json_y - 0.55, "Output", (0.5, 0))
    # D1 -> D2 (right, Input)
    draw_arrow(d1_x + 1.8, d1_y, d2_x - 1.8, d2_y, "Input", (0, 0.4))
    # D2 -> YAML1 (down, No)
    draw_arrow(d2_x, d2_y - 1.5, yaml1_x, yaml1_y + 0.55, "No", (0.5, 0))
    # D2 -> D3 (right, Yes)
    draw_arrow(d2_x + 1.8, d2_y, d3_x - 1.8, d3_y, "Yes", (0, 0.4))
    # D3 -> YAML2 (up, No)
    draw_arrow(d3_x, d3_y + 1.5, yaml2_x, yaml2_y - 0.55, "No", (0.5, 0))
    # D3 -> TOON (right, Yes)
    draw_arrow(d3_x + 1.8, d3_y, toon_x - 1.3, toon_y, "Yes", (0, 0.4))

    plt.tight_layout(pad=1)
    save_figure(fig, "../graphics/graph_9_decision_flowchart")
    plt.close()


if __name__ == "__main__":
    graph_9_decision_flowchart()
