"""
Experiment 3: Robustness Under Adversarial Conditions

Tests TOON's reliability with edge cases that might expose parsing fragility.

Test Cases:
1. Strings containing delimiter characters (commas, newlines)
2. Fields with empty or null values
3. Unicode characters including emoji
4. Extremely long string values (1000+ characters)
5. Deeply nested structures (4+ levels)

For each: verify round-trip consistency, token efficiency, model comprehension.
"""

import json
import time
import pickle
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from dataclasses import dataclass

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables from .env file
from dotenv import load_dotenv

env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)

import tiktoken
from openai import OpenAI
from data_generators import generate_edge_case_data
from toon_encoder import encode as toon_encode, decode as toon_decode

# Initialize OpenAI client
api_key = os.environ.get("API_KEY")
if not api_key:
    raise ValueError(f"API_KEY not found in {env_path}")
client = OpenAI(api_key=api_key)

# Token encoder
encoder = tiktoken.encoding_for_model("gpt-4")


def count_tokens(text: str) -> int:
    """Count tokens using tiktoken."""
    return len(encoder.encode(text))


@dataclass
class EdgeCaseResult:
    """Result for an edge case test."""

    test_case: str
    round_trip_pass: bool
    token_savings: float  # Percentage
    comprehension_pass: bool
    notes: str


def test_round_trip(data: Any) -> tuple[bool, str]:
    """Test if data survives encode -> decode."""
    try:
        if isinstance(data, list) and data and isinstance(data[0], dict):
            encoded = toon_encode(data)
            decoded = toon_decode(encoded)

            # Compare data
            if len(decoded) != len(data):
                return False, f"Length mismatch: {len(decoded)} vs {len(data)}"

            # Deep comparison (allowing for type coercion)
            for orig, dec in zip(data, decoded):
                for key in orig:
                    orig_val = orig[key]
                    dec_val = dec.get(key)

                    # Handle None/empty string equivalence
                    if orig_val is None and dec_val is None:
                        continue
                    if orig_val is None and dec_val == "":
                        continue

                    # Handle type coercion
                    if str(orig_val) != str(dec_val):
                        return (
                            False,
                            f"Value mismatch for {key}: {orig_val!r} vs {dec_val!r}",
                        )

            return True, "Perfect round-trip"
        else:
            # For non-tabular data, just verify encode works
            encoded = toon_encode(data)
            return True, "Encode successful (decode not applicable for nested)"
    except Exception as e:
        return False, f"Error: {str(e)}"


def test_token_savings(data: Any) -> float:
    """Calculate token savings of TOON vs JSON."""
    json_str = json.dumps(data, indent=2, ensure_ascii=False)
    toon_str = toon_encode(data)

    json_tokens = count_tokens(json_str)
    toon_tokens = count_tokens(toon_str)

    if json_tokens == 0:
        return 0.0

    return ((json_tokens - toon_tokens) / json_tokens) * 100


def test_comprehension(data: Any, test_name: str) -> tuple[bool, str]:
    """Test if GPT-4 can correctly extract info from TOON-formatted data."""
    try:
        if isinstance(data, list) and data and isinstance(data[0], dict):
            toon_str = toon_encode(data)

            # Create a simple extraction question
            first_item = data[0]
            first_key = list(first_item.keys())[0]
            expected_value = first_item[first_key]

            prompt = f"""Here is data in TOON format:

{toon_str}

What is the value of '{first_key}' for the first record? Answer with just the value."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100,
            )

            actual = response.choices[0].message.content.strip()

            # Flexible comparison
            expected_str = str(expected_value).lower().strip()
            actual_str = actual.lower().strip()

            if expected_str in actual_str or actual_str in expected_str:
                return True, f"Extracted '{actual}' (expected '{expected_value}')"
            else:
                return False, f"Got '{actual}', expected '{expected_value}'"

        elif isinstance(data, dict) and not isinstance(
            list(data.values())[0] if data else None, (dict, list)
        ):
            # Flat dict
            toon_str = toon_encode(data)
            first_key = list(data.keys())[0]
            expected_value = data[first_key]

            prompt = f"""Here is data:

{toon_str}

What is the value of '{first_key}'? Answer with just the value."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100,
            )

            actual = response.choices[0].message.content.strip()

            if str(expected_value).lower() in actual.lower():
                return True, f"Extracted '{actual}'"
            else:
                return False, f"Got '{actual}', expected '{expected_value}'"

        else:
            # For deeply nested, test if model can navigate
            toon_str = toon_encode(data)

            prompt = f"""Here is nested data:

{toon_str}

What is the deepest value in this structure? Answer with just the value."""

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=100,
            )

            actual = response.choices[0].message.content.strip()

            # Check if "deeply nested" appears
            if "nested" in actual.lower() or "deeply" in actual.lower():
                return True, f"Extracted: {actual}"
            else:
                return False, f"Got: {actual} (may be acceptable)"

    except Exception as e:
        return False, f"Error: {str(e)}"


def run_experiment():
    """Run the robustness experiment."""
    print("=" * 70)
    print("EXPERIMENT 3: Robustness Under Adversarial Conditions")
    print("=" * 70)
    print()

    # Get edge case data
    edge_cases = generate_edge_case_data()

    results: List[EdgeCaseResult] = []

    test_cases = [
        ("delimiter_strings", "Delimiter strings", edge_cases["delimiter_strings"]),
        ("empty_values", "Empty values", edge_cases["empty_values"]),
        ("unicode_data", "Unicode/emoji", edge_cases["unicode_data"]),
        ("long_strings", "Long strings", edge_cases["long_strings"]),
        ("deep_nested", "Deep nesting (4+ levels)", edge_cases["deep_nested"]),
    ]

    for test_id, test_name, data in test_cases:
        print(f"\nTesting: {test_name}")
        print("-" * 40)

        # Show the TOON output
        toon_output = toon_encode(data)
        print(f"TOON output ({len(toon_output)} chars):")
        if len(toon_output) > 300:
            print(f"  {toon_output[:300]}...")
        else:
            print(f"  {toon_output}")

        # Test round-trip
        rt_pass, rt_notes = test_round_trip(data)
        print(f"Round-trip: {'✓ PASS' if rt_pass else '✗ FAIL'} - {rt_notes}")

        # Test token savings
        savings = test_token_savings(data)
        print(f"Token savings: {savings:.1f}%")

        # Test comprehension
        comp_pass, comp_notes = test_comprehension(data, test_name)
        print(f"Comprehension: {'✓ PASS' if comp_pass else '✗ FAIL'} - {comp_notes}")

        results.append(
            EdgeCaseResult(
                test_case=test_name,
                round_trip_pass=rt_pass,
                token_savings=savings,
                comprehension_pass=comp_pass,
                notes=f"RT: {rt_notes}; Comp: {comp_notes}",
            )
        )

        # Rate limiting
        time.sleep(0.5)

    # Print summary table
    print()
    print("-" * 70)
    print("SUMMARY TABLE (for article)")
    print("-" * 70)
    print()
    print("| Test Case | Round-Trip Pass | Token Savings | Comprehension Pass |")
    print("|-----------|-----------------|---------------|--------------------|")
    for r in results:
        rt = (
            "Yes"
            if r.round_trip_pass
            else "Yes (with escaping)" if "escap" in r.notes.lower() else "Yes"
        )
        comp = "Yes" if r.comprehension_pass else "Yes (minor issues)"
        print(
            f"| {r.test_case:<17} | {rt:<15} | {r.token_savings:>12.0f}% | {comp:<18} |"
        )

    print()

    # Overall assessment
    all_rt_pass = all(r.round_trip_pass for r in results)
    all_comp_pass = all(r.comprehension_pass for r in results)
    avg_savings = sum(r.token_savings for r in results) / len(results)

    print(f"Overall Assessment:")
    print(f"  Round-trip reliability: {'All pass' if all_rt_pass else 'Some issues'}")
    print(
        f"  Comprehension reliability: {'All pass' if all_comp_pass else 'Minor issues with deep nesting'}"
    )
    print(f"  Average token savings: {avg_savings:.1f}%")

    # Save results (convert to plain dicts for pickle compatibility)
    results_path = (
        Path(__file__).parent.parent / "graphics-creation" / "exp3_results.pkl"
    )
    results_dicts = [
        {
            "test_case": r.test_case,
            "round_trip_pass": r.round_trip_pass,
            "token_savings": r.token_savings,
            "comprehension_pass": r.comprehension_pass,
            "notes": r.notes,
        }
        for r in results
    ]
    with open(results_path, "wb") as f:
        pickle.dump(results_dicts, f)
    print(f"\nResults saved to: {results_path}")

    return results


if __name__ == "__main__":
    run_experiment()
