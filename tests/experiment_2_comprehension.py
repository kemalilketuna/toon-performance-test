"""
Experiment 2 V2: Comprehension Validation

Redesigned to properly test format differences with:
- Smaller dataset (20 products) for more reliable responses
- Query types that differentiate formats
- Better evaluation methodology
"""

import json
import time
import pickle
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass
from statistics import mean, stdev
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

from data_generators import generate_products
from toon_encoder import encode as toon_encode

from openai import OpenAI

api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError(f"API_KEY not found in {env_path}")
client = OpenAI(api_key=api_key)


@dataclass
class TrialResult:
    format_type: str
    query_type: str
    expected: Any
    actual: Any
    match_type: str
    latency: float
    raw_response: str


def serialize_json(data: list) -> str:
    return json.dumps({"products": data}, indent=2)


def serialize_toon(data: list) -> str:
    return f"products{toon_encode(data)}"


def compute_ground_truth(
    products: List[Dict], query_type: str, query_params: Dict
) -> Any:
    if query_type == "price_lookup":
        target_id = query_params["id"]
        for p in products:
            if p["id"] == target_id:
                return p["price"]
        return None

    elif query_type == "product_by_index":
        # What is the Nth product's name?
        idx = query_params["index"]
        if 0 <= idx < len(products):
            return products[idx]["name"]
        return None

    elif query_type == "category_of_product":
        # What category is product ID X in?
        target_id = query_params["id"]
        for p in products:
            if p["id"] == target_id:
                return p["category"]
        return None

    elif query_type == "stock_check":
        # What is the stock of product with name X?
        target_name = query_params["name"]
        for p in products:
            if p["name"] == target_name:
                return p["stock"]
        return None

    elif query_type == "find_cheapest":
        # What is the cheapest product in category X?
        target_cat = query_params["category"]
        cat_products = [p for p in products if p["category"] == target_cat]
        if cat_products:
            cheapest = min(cat_products, key=lambda p: p["price"])
            return cheapest["name"]
        return None

    return None


def build_prompt(data_str: str, query_type: str, query_params: Dict) -> str:
    if query_type == "price_lookup":
        question = f"What is the price of the product with ID {query_params['id']}? Reply with just the number."
    elif query_type == "product_by_index":
        question = f"What is the name of product #{query_params['index'] + 1} in the list? Reply with just the name."
    elif query_type == "category_of_product":
        question = f"What category is the product with ID {query_params['id']} in? Reply with just the category name."
    elif query_type == "stock_check":
        question = f"What is the stock quantity of the product named '{query_params['name']}'? Reply with just the number."
    elif query_type == "find_cheapest":
        question = f"Which product in the {query_params['category']} category has the lowest price? Reply with just the product name."
    else:
        raise ValueError(f"Unknown query type: {query_type}")

    return f"""Here is product data:

{data_str}

Question: {question}"""


def parse_response(response: str, query_type: str) -> Any:
    response = response.strip().strip("\"'")

    if query_type in ["price_lookup"]:
        import re

        cleaned = response.replace("$", "").replace(",", "")
        match = re.search(r"[\d.]+", cleaned)
        if match:
            return float(match.group())
        return None

    elif query_type in ["stock_check"]:
        import re

        match = re.search(r"\d+", response)
        if match:
            return int(match.group())
        return None

    elif query_type in [
        "product_by_index",
        "category_of_product",
        "stock_check",
        "find_cheapest",
    ]:
        # Clean up response
        response = response.strip()
        # Remove common prefixes
        for prefix in [
            "The ",
            "the ",
            "It is ",
            "it is ",
            "Product: ",
            "Name: ",
            "Category: ",
        ]:
            if response.startswith(prefix):
                response = response[len(prefix) :]
        return response.strip()

    return response


def evaluate_match(expected: Any, actual: Any, query_type: str) -> str:
    if actual is None:
        return "failure"

    if query_type == "price_lookup":
        try:
            if abs(float(expected) - float(actual)) < 0.01:
                return "exact"
            elif abs(float(expected) - float(actual)) < 5.0:
                return "partial"
        except:
            pass
        return "failure"

    elif query_type == "stock_check":
        try:
            if int(expected) == int(actual):
                return "exact"
            elif abs(int(expected) - int(actual)) <= 5:
                return "partial"
        except:
            pass
        return "failure"

    elif query_type in ["product_by_index", "category_of_product", "find_cheapest"]:
        expected_str = str(expected).lower().strip()
        actual_str = str(actual).lower().strip()

        if expected_str == actual_str:
            return "exact"
        # Check if one contains the other (for partial matches)
        if expected_str in actual_str or actual_str in expected_str:
            return "partial"
        # Check for close match (e.g., with/without extra words)
        expected_words = set(expected_str.split())
        actual_words = set(actual_str.split())
        if expected_words & actual_words:  # Some overlap
            overlap = len(expected_words & actual_words) / len(expected_words)
            if overlap >= 0.5:
                return "partial"
        return "failure"

    return "failure"


def run_trial(
    data_str: str,
    format_type: str,
    query_type: str,
    query_params: Dict,
    expected: Any,
    verbose: bool = False,
) -> TrialResult:
    prompt = build_prompt(data_str, query_type, query_params)

    start_time = time.time()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            max_tokens=100,
        )
        raw_response = response.choices[0].message.content
    except Exception as e:
        raw_response = f"ERROR: {str(e)}"

    latency = time.time() - start_time

    actual = parse_response(raw_response, query_type)
    match_type = evaluate_match(expected, actual, query_type)

    if verbose and match_type == "failure":
        print(
            f"\n    FAILURE: Expected='{expected}', Got='{actual}', Raw='{raw_response[:80]}'"
        )

    return TrialResult(
        format_type=format_type,
        query_type=query_type,
        expected=expected,
        actual=actual,
        match_type=match_type,
        latency=latency,
        raw_response=raw_response,
    )


def run_experiment(
    n_products: int = 20, trials_per_query: int = 20, verbose: bool = False
):
    print("=" * 70)
    print("EXPERIMENT 2 V2: Comprehension Validation")
    print("=" * 70)
    print()

    products = generate_products(n_products, seed=42)

    json_str = serialize_json(products)
    toon_str = serialize_toon(products)

    print(f"Dataset: {n_products} products")
    print(f"Data sizes: JSON={len(json_str)} chars, TOON={len(toon_str)} chars")
    print(f"Compression: {100*(1 - len(toon_str)/len(json_str)):.1f}% smaller")
    print()

    # Category distribution
    from collections import Counter

    cats = Counter(p["category"] for p in products)
    target_category = max(cats, key=cats.get)

    # Define queries
    queries = [
        {
            "type": "price_lookup",
            "params": {"id": products[5]["id"]},
            "description": f"Price of product ID {products[5]['id']}",
        },
        {
            "type": "product_by_index",
            "params": {"index": 7},
            "description": "Name of 8th product in list",
        },
        {
            "type": "category_of_product",
            "params": {"id": products[12]["id"]},
            "description": f"Category of product ID {products[12]['id']}",
        },
        {
            "type": "stock_check",
            "params": {"name": products[3]["name"]},
            "description": f"Stock of '{products[3]['name']}'",
        },
        {
            "type": "find_cheapest",
            "params": {"category": target_category},
            "description": f"Cheapest product in {target_category}",
        },
    ]

    # Compute ground truth
    print("Queries:")
    for query in queries:
        query["expected"] = compute_ground_truth(
            products, query["type"], query["params"]
        )
        print(f"  {query['description']}: {query['expected']}")
    print()

    results: List[TrialResult] = []
    formats = [("JSON", json_str), ("TOON", toon_str)]

    total_trials = len(formats) * len(queries) * trials_per_query
    print(
        f"Running {total_trials} trials ({trials_per_query} per query × {len(queries)} queries × 2 formats)..."
    )
    print()

    for format_name, data_str in formats:
        print(f"{format_name}:")
        for query in queries:
            print(f"  {query['type'][:20]:<20}...", end=" ", flush=True)
            query_results = []

            for trial_num in range(trials_per_query):
                result = run_trial(
                    data_str=data_str,
                    format_type=format_name,
                    query_type=query["type"],
                    query_params=query["params"],
                    expected=query["expected"],
                    verbose=verbose and trial_num == 0,
                )
                results.append(result)
                query_results.append(result)
                time.sleep(0.05)

            exact = sum(1 for r in query_results if r.match_type == "exact")
            partial = sum(1 for r in query_results if r.match_type == "partial")
            failure = sum(1 for r in query_results if r.match_type == "failure")
            avg_latency = mean(r.latency for r in query_results)

            print(
                f"exact={exact:2d}/{trials_per_query}, partial={partial:2d}, fail={failure:2d} | {avg_latency:.2f}s"
            )
        print()

    # Aggregate
    print("-" * 70)
    print("AGGREGATED RESULTS")
    print("-" * 70)

    summary = {}
    for format_name in ["JSON", "TOON"]:
        format_results = [r for r in results if r.format_type == format_name]
        total = len(format_results)

        exact_count = sum(1 for r in format_results if r.match_type == "exact")
        partial_count = sum(1 for r in format_results if r.match_type == "partial")
        failure_count = sum(1 for r in format_results if r.match_type == "failure")
        latencies = [r.latency for r in format_results]

        summary[format_name] = {
            "exact_rate": 100 * exact_count / total,
            "partial_rate": 100 * partial_count / total,
            "failure_rate": 100 * failure_count / total,
            "avg_latency": mean(latencies),
            "std_latency": stdev(latencies) if len(latencies) > 1 else 0,
            "latencies": latencies,
        }

        print(f"\n{format_name}:")
        print(f"  Exact:   {summary[format_name]['exact_rate']:.1f}%")
        print(f"  Partial: {summary[format_name]['partial_rate']:.1f}%")
        print(f"  Failure: {summary[format_name]['failure_rate']:.1f}%")
        print(
            f"  Latency: {summary[format_name]['avg_latency']:.2f}s (±{summary[format_name]['std_latency']:.2f}s)"
        )

    print()
    print("-" * 70)
    print("SUMMARY TABLE")
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

    # Analysis
    print()
    json_exact = summary["JSON"]["exact_rate"]
    toon_exact = summary["TOON"]["exact_rate"]
    json_lat = summary["JSON"]["avg_latency"]
    toon_lat = summary["TOON"]["avg_latency"]

    print(f"TOON vs JSON:")
    print(f"  Accuracy diff: {toon_exact - json_exact:+.1f} percentage points")
    print(f"  Latency improvement: {100*(json_lat - toon_lat)/json_lat:.1f}%")

    # Save results
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
    parser.add_argument("--products", type=int, default=20)
    parser.add_argument("--trials", type=int, default=20)
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    run_experiment(
        n_products=args.products, trials_per_query=args.trials, verbose=args.verbose
    )
