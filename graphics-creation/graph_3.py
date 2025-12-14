"""
Graph 3: Savings Scaling Line Graph

Line graph showing how savings scale with record count.
"""

import matplotlib.pyplot as plt

from style import COLORS, apply_style, save_figure
from common import load_results


def graph_3_savings_scaling(results=None):
    """Line graph showing how savings scale with record count."""
    apply_style()

    if results is None:
        results = load_results()

    if "exp1" not in results:
        print("Skipping Graph 3: No experiment 1 results")
        return

    data = results["exp1"]
    records = [d["records"] for d in data]
    toon_savings = [d["toon_savings"] for d in data]
    yaml_savings = [d["yaml_savings"] for d in data]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        records,
        toon_savings,
        "o-",
        color=COLORS["TOON"],
        linewidth=2,
        markersize=8,
        label="TOON",
    )
    ax.plot(
        records,
        yaml_savings,
        "s--",
        color=COLORS["YAML"],
        linewidth=2,
        markersize=8,
        label="YAML",
    )

    ax.axhline(y=0, color=COLORS["neutral"], linestyle="-", linewidth=0.5)

    ax.set_xlabel("Number of Records")
    ax.set_ylabel("Token Savings vs JSON (%)")
    ax.set_title("Token Efficiency Scaling: TOON vs YAML", fontweight="bold")
    ax.legend(loc="right")

    ax.set_ylim(0, 80)
    ax.fill_between(records, toon_savings, alpha=0.2, color=COLORS["TOON"])
    ax.fill_between(records, yaml_savings, alpha=0.2, color=COLORS["YAML"])

    plt.tight_layout()
    save_figure(fig, "../graphics/graph_3_savings_scaling")
    plt.close()


if __name__ == "__main__":
    graph_3_savings_scaling()
