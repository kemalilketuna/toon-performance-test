"""
Generate all graphics for the TOON article.

Run with: python graphics/generate_all.py
"""

from common import load_results

from graph_1 import graph_1_token_breakdown
from graph_2 import graph_2_token_counts
from graph_3 import graph_3_savings_scaling
from graph_4 import graph_4_accuracy
from graph_5 import graph_5_latency
from graph_6 import graph_6_cost_projection
from graph_7 import graph_7_reliability
from graph_8 import graph_8_architecture
from graph_9 import graph_9_decision_flowchart
from graph_10 import graph_10_summary


def main():
    print("=" * 60)
    print("Generating all article graphics...")
    print("=" * 60)
    print()

    results = load_results()
    print(f"Loaded results: {list(results.keys())}")
    print()

    # Generate all graphs
    print("Graph 1: Token Breakdown Diagram...")
    graph_1_token_breakdown()

    print("Graph 2: Token Counts Bar Chart...")
    graph_2_token_counts(results)

    print("Graph 3: Savings Scaling Line Graph...")
    graph_3_savings_scaling(results)

    print("Graph 4: Accuracy Comparison...")
    graph_4_accuracy(results)

    print("Graph 5: Latency Distribution...")
    graph_5_latency(results)

    print("Graph 6: Cost Projection...")
    graph_6_cost_projection(results)

    print("Graph 7: Reliability Cascade...")
    graph_7_reliability(results)

    print("Graph 8: Architecture Diagram...")
    graph_8_architecture()

    print("Graph 9: Decision Flowchart...")
    graph_9_decision_flowchart()

    print("Graph 10: Summary Infographic...")
    graph_10_summary(results)

    print()
    print("=" * 60)
    print("All graphics generated successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
