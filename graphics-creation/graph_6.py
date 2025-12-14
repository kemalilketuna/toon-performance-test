"""
Graph 6: Cost Projection

Area chart showing cumulative cost savings over time.
"""

import matplotlib.pyplot as plt
import numpy as np

from style import COLORS, apply_style, save_figure
from common import load_results


def graph_6_cost_projection(results=None):
    """Area chart showing cumulative cost savings over time."""
    apply_style()

    if results is None:
        results = load_results()

    if "exp1" not in results:
        print("Skipping Graph 6: No experiment 1 results")
        return

    # Use the 500-record savings rate as representative
    data = results["exp1"]
    savings_rate = data[-1]["toon_savings"] / 100  # ~67%

    # Monthly tokens for different query volumes (at 2K tokens per query)
    volumes = {
        "100K queries/day": 100_000 * 2000 * 30,
        "500K queries/day": 500_000 * 2000 * 30,
        "1M queries/day": 1_000_000 * 2000 * 30,
    }

    cost_per_1k = 0.01  # $0.01 per 1K tokens
    months = np.arange(1, 13)

    fig, ax = plt.subplots(figsize=(10, 6))

    colors = [COLORS["TOON"], COLORS["YAML"], COLORS["JSON"]]
    alphas = [0.8, 0.5, 0.3]

    for i, (label, monthly_tokens) in enumerate(volumes.items()):
        monthly_cost_json = (monthly_tokens / 1000) * cost_per_1k
        monthly_savings = monthly_cost_json * savings_rate
        cumulative_savings = months * monthly_savings

        ax.fill_between(
            months,
            cumulative_savings / 1000,
            alpha=alphas[i],
            color=colors[i],
            label=f"{label}: ${cumulative_savings[-1]/1000:.0f}K/year",
        )
        ax.plot(months, cumulative_savings / 1000, color=colors[i], linewidth=2)

    ax.set_xlabel("Month")
    ax.set_ylabel("Cumulative Savings ($K)")
    ax.set_title("Projected Annual Savings from TOON Adoption", fontweight="bold")
    ax.legend(loc="upper left")
    ax.set_xlim(1, 12)
    ax.set_xticks(months)

    plt.tight_layout()
    save_figure(fig, "../graphics/graph_6_cost_projection")
    plt.close()


if __name__ == "__main__":
    graph_6_cost_projection()
