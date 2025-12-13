"""
Experiment 2: Comprehension Validation

Tests GPT-4's accuracy at extracting information from TOON vs JSON formatted data.

Test Design:
- Dataset: 50 product records (id, name, category, price, stock)
- Model: GPT-4 (temperature=0)
- Query types: specific retrieval, category filtering, aggregation
- Trials: 100 runs per query per format (600 total API calls)
- Evaluation: Exact match, partial match, failure rates
"""

import json
import time
import pickle
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
from statistics import mean, stdev

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from data_generators import generate_products
from toon_encoder import encode as toon_encode

# Initialize OpenAI client
from openai import OpenAI

api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError(f"API_KEY not found in {env_path}")
client = OpenAI(api_key=api_key)


@dataclass
class TrialResult:
    """Result of a single trial."""

    format_type: str
    query_type: str
    expected: Any
    actual: Any
    match_type: str  # "exact", "partial", "failure"
    latency: float
    raw_response: str


def serialize_json(data: list) -> str:
    """Serialize products to JSON."""
    return json.dumps({"products": data}, indent=2)


def serialize_toon(data: list) -> str:
    """Serialize products to TOON format."""
    return f"products{toon_encode(data)}"


def compute_ground_truth(
    products: List[Dict], query_type: str, query_params: Dict
) -> Any:
    """Compute expected answer programmatically."""
    if query_type == "specific_retrieval":
        target_id = query_params["id"]
        for p in products:
            if p["id"] == target_id:
                return p["price"]
        return None

    elif query_type == "category_filter":
        target_category = query_params["category"]
        return [p["name"] for p in products if p["category"] == target_category]

    elif query_type == "aggregation":
        threshold = query_params["price_threshold"]
        return sum(p["stock"] for p in products if p["price"] > threshold)

    return None


def build_prompt(data_str: str, query_type: str, query_params: Dict) -> str:
    """Build the prompt for GPT-4."""
    if query_type == "specific_retrieval":
        question = f"What is the price of the product with ID {query_params['id']}? Answer with just the number."
    elif query_type == "category_filter":
        question = f"List all product names in the {query_params['category']} category. Answer with a comma-separated list of names only."
    elif query_type == "aggregation":
        question = f"What is the total stock quantity for all products priced over ${query_params['price_threshold']}? Answer with just the number."
    else:
        raise ValueError(f"Unknown query type: {query_type}")

    return f"""Here is product data:

{data_str}

Question: {question}"""


def parse_response(response: str, query_type: str) -> Any:
    """Parse the model's response to extract the answer."""
    response = response.strip()

    if query_type == "specific_retrieval":
        # Extract number from response
        try:
            # Remove any currency symbols or extra text
            cleaned = response.replace("$", "").replace(",", "").strip()
            # Try to find a number
            import re

            match = re.search(r"[\d.]+", cleaned)
            if match:
                return float(match.group())
        except:
            pass
        return None

    elif query_type == "category_filter":
        # Parse comma-separated list
        names = [n.strip() for n in response.split(",")]
        return [n for n in names if n]  # Remove empty strings

    elif query_type == "aggregation":
        try:
            cleaned = response.replace(",", "").strip()
            import re

            match = re.search(r"\d+", cleaned)
            if match:
                return int(match.group())
        except:
            pass
        return None

    return response


def evaluate_match(expected: Any, actual: Any, query_type: str) -> str:
    """Evaluate if the response matches the expected answer."""
    if actual is None:
        return "failure"

    if query_type == "specific_retrieval":
        if expected is None:
            return "failure"
        try:
            if abs(float(expected) - float(actual)) < 0.01:
                return "exact"
            elif abs(float(expected) - float(actual)) < 1.0:
                return "partial"
        except:
            pass
        return "failure"

    elif query_type == "category_filter":
        if not isinstance(actual, list):
            return "failure"
        expected_set = set(expected)
        actual_set = set(actual)

        if expected_set == actual_set:
            return "exact"
        elif len(expected_set & actual_set) > 0:
            overlap = len(expected_set & actual_set) / len(expected_set)
            return "partial" if overlap > 0.5 else "failure"
        return "failure"

    elif query_type == "aggregation":
        if expected is None:
            return "failure"
        try:
            if int(expected) == int(actual):
                return "exact"
            # Allow 5% tolerance for partial match
            elif abs(int(expected) - int(actual)) / max(int(expected), 1) < 0.05:
                return "partial"
        except:
            pass
        return "failure"

    return "failure"


def run_trial(
    data_str: str, format_type: str, query_type: str, query_params: Dict, expected: Any
) -> TrialResult:
    """Run a single trial."""
    prompt = build_prompt(data_str, query_type, query_params)

    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # Using gpt-4o-mini for cost efficiency, still representative
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=500,
        )
        raw_response = response.choices[0].message.content
    except Exception as e:
        raw_response = f"ERROR: {str(e)}"

    latency = time.time() - start_time

    actual = parse_response(raw_response, query_type)
    match_type = evaluate_match(expected, actual, query_type)

    return TrialResult(
        format_type=format_type,
        query_type=query_type,
        expected=expected,
        actual=actual,
        match_type=match_type,
        latency=latency,
        raw_response=raw_response,
    )


def run_experiment(trials_per_query: int = 100):
    """Run the full comprehension experiment."""
    print("=" * 70)
    print("EXPERIMENT 2: Comprehension Validation")
    print("=" * 70)
    print()

    # Generate 50 product records
    products = generate_products(50, seed=42)

    # Prepare serializations
    json_str = serialize_json(products)
    toon_str = serialize_toon(products)

    print(f"Data sizes:")
    print(f"  JSON: {len(json_str)} chars")
    print(f"  TOON: {len(toon_str)} chars")
    print()

    # Define queries
    # Pick a product ID that exists
    target_product = products[36]  # ID 37 (0-indexed at 36)
    electronics_products = [p for p in products if p["category"] == "Electronics"]

    queries = [
        {
            "type": "specific_retrieval",
            "params": {"id": 37},
            "description": f"What is the price of product ID 37?",
        },
        {
            "type": "category_filter",
            "params": {"category": "Electronics"},
            "description": "Which products are in Electronics category?",
        },
        {
            "type": "aggregation",
            "params": {"price_threshold": 100},
            "description": "Total stock for products priced over $100?",
        },
    ]

    # Compute ground truth
    for query in queries:
        query["expected"] = compute_ground_truth(
            products, query["type"], query["params"]
        )
        print(f"Query: {query['description']}")
        print(f"  Ground truth: {query['expected']}")
    print()

    results: List[TrialResult] = []
    formats = [("JSON", json_str), ("TOON", toon_str)]

    total_trials = len(formats) * len(queries) * trials_per_query
    completed = 0

    print(f"Running {total_trials} trials ({trials_per_query} per query per format)...")
    print()

    for format_name, data_str in formats:
        for query in queries:
            print(f"  {format_name} - {query['type']}...", end=" ", flush=True)
            query_results = []

            for trial_num in range(trials_per_query):
                result = run_trial(
                    data_str=data_str,
                    format_type=format_name,
                    query_type=query["type"],
                    query_params=query["params"],
                    expected=query["expected"],
                )
                results.append(result)
                query_results.append(result)
                completed += 1

                # Rate limiting
                time.sleep(0.1)

            # Print intermediate results
            exact = sum(1 for r in query_results if r.match_type == "exact")
            partial = sum(1 for r in query_results if r.match_type == "partial")
            failure = sum(1 for r in query_results if r.match_type == "failure")
            avg_latency = mean(r.latency for r in query_results)

            print(
                f"exact={exact}/{trials_per_query} ({100*exact/trials_per_query:.1f}%), "
                f"partial={partial}, failure={failure}, latency={avg_latency:.2f}s"
            )

    print()

    # Aggregate results
    print("-" * 70)
    print("AGGREGATED RESULTS")
    print("-" * 70)
    print()

    summary = {}
    for format_name in ["JSON", "TOON"]:
        format_results = [r for r in results if r.format_type == format_name]

        exact_count = sum(1 for r in format_results if r.match_type == "exact")
        partial_count = sum(1 for r in format_results if r.match_type == "partial")
        failure_count = sum(1 for r in format_results if r.match_type == "failure")
        total = len(format_results)

        latencies = [r.latency for r in format_results]

        summary[format_name] = {
            "exact_rate": 100 * exact_count / total,
            "partial_rate": 100 * partial_count / total,
            "failure_rate": 100 * failure_count / total,
            "avg_latency": mean(latencies),
            "std_latency": stdev(latencies) if len(latencies) > 1 else 0,
            "latencies": latencies,
        }

        print(f"{format_name}:")
        print(f"  Exact Match:   {summary[format_name]['exact_rate']:.1f}%")
        print(f"  Partial Match: {summary[format_name]['partial_rate']:.1f}%")
        print(f"  Failure Rate:  {summary[format_name]['failure_rate']:.1f}%")
        print(
            f"  Avg Latency:   {summary[format_name]['avg_latency']:.2f}s (±{summary[format_name]['std_latency']:.2f}s)"
        )
        print()

    # Print table for article
    print("-" * 70)
    print("SUMMARY TABLE (for article)")
    print("-" * 70)
    print()
    print(
        "| Format | Exact Match Rate | Partial Match Rate | Failure Rate | Avg. Latency |"
    )
    print(
        "|--------|------------------|--------------------| -------------|--------------|"
    )
    for fmt in ["JSON", "TOON"]:
        s = summary[fmt]
        print(
            f"| {fmt:<6} | {s['exact_rate']:>15.1f}% | {s['partial_rate']:>17.1f}% | {s['failure_rate']:>11.1f}% | {s['avg_latency']:>11.2f}s |"
        )

    print()

    # Calculate improvement
    json_exact = summary["JSON"]["exact_rate"]
    toon_exact = summary["TOON"]["exact_rate"]
    accuracy_diff = toon_exact - json_exact

    json_latency = summary["JSON"]["avg_latency"]
    toon_latency = summary["TOON"]["avg_latency"]
    latency_improvement = ((json_latency - toon_latency) / json_latency) * 100

    print(f"TOON vs JSON:")
    print(f"  Accuracy difference: {accuracy_diff:+.1f} percentage points")
    print(f"  Latency improvement: {latency_improvement:.1f}%")

    # Save results for graph generation (convert to plain dicts for pickle compatibility)
    results_path = (
        Path(__file__).parent.parent / "graphics-creation" / "exp2_results.pkl"
    )
    raw_results_dicts = [
        {
            "format_type": r.format_type,
            "query_type": r.query_type,
            "match_type": r.match_type,
            "latency": r.latency,
        }
        for r in results
    ]
    with open(results_path, "wb") as f:
        pickle.dump({"summary": summary, "raw_results": raw_results_dicts}, f)
    print(f"\nResults saved to: {results_path}")

    return summary, results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--trials",
        type=int,
        default=100,
        help="Number of trials per query per format (default: 100)",
    )
    args = parser.parse_args()

    run_experiment(trials_per_query=args.trials)
