"""
Experiment 1: Token Consumption at Scale

Measures token efficiency of JSON, YAML, and TOON across varying dataset sizes.

Test Design:
- Datasets: 10, 50, 100, 250, 500 user records
- Record structure: id, name, email, role, active
- Formats: JSON, YAML, TOON
- Measurement: tiktoken with cl100k_base encoding
"""

import json
import yaml
import tiktoken
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from data_generators import generate_users
from toon_encoder import encode as toon_encode


def count_tokens(text: str, model: str = "gpt-4") -> int:
    """Count tokens using tiktoken."""
    encoder = tiktoken.encoding_for_model(model)
    return len(encoder.encode(text))


def serialize_json(data: list) -> str:
    """Serialize to formatted JSON (standard formatting)."""
    return json.dumps(data, indent=2)


def serialize_yaml(data: list) -> str:
    """Serialize to YAML."""
    return yaml.dump(data, default_flow_style=False, allow_unicode=True)


def serialize_toon(data: list) -> str:
    """Serialize to TOON format."""
    return toon_encode(data)


def run_experiment():
    """Run the token consumption experiment."""
    dataset_sizes = [10, 50, 100, 250, 500]
    results = []

    print("=" * 70)
    print("EXPERIMENT 1: Token Consumption at Scale")
    print("=" * 70)
    print()

    for n in dataset_sizes:
        # Generate consistent data
        data = generate_users(n, seed=42)

        # Wrap in container like the article example
        data_wrapped = {"users": data}

        # Serialize to each format
        json_str = serialize_json(data_wrapped)
        yaml_str = serialize_yaml(data_wrapped)
        toon_str = f"users{toon_encode(data)}"  # Add the 'users' prefix

        # Count tokens
        json_tokens = count_tokens(json_str)
        yaml_tokens = count_tokens(yaml_str)
        toon_tokens = count_tokens(toon_str)

        # Calculate savings
        toon_savings_vs_json = ((json_tokens - toon_tokens) / json_tokens) * 100
        yaml_savings_vs_json = ((json_tokens - yaml_tokens) / json_tokens) * 100

        results.append(
            {
                "records": n,
                "json_tokens": json_tokens,
                "yaml_tokens": yaml_tokens,
                "toon_tokens": toon_tokens,
                "toon_savings": toon_savings_vs_json,
                "yaml_savings": yaml_savings_vs_json,
            }
        )

        print(f"Records: {n}")
        print(f"  JSON:  {json_tokens:,} tokens")
        print(f"  YAML:  {yaml_tokens:,} tokens ({yaml_savings_vs_json:.1f}% savings)")
        print(f"  TOON:  {toon_tokens:,} tokens ({toon_savings_vs_json:.1f}% savings)")
        print()

    # Print summary table
    print("-" * 70)
    print("SUMMARY TABLE (for article)")
    print("-" * 70)
    print()
    print(
        "| Records | JSON Tokens | YAML Tokens | TOON Tokens | TOON Savings vs JSON |"
    )
    print(
        "|---------|-------------|-------------|-------------|----------------------|"
    )
    for r in results:
        print(
            f"| {r['records']:>7} | {r['json_tokens']:>11,} | {r['yaml_tokens']:>11,} | {r['toon_tokens']:>11,} | {r['toon_savings']:>19.1f}% |"
        )

    print()
    print("-" * 70)
    print("FORMAT EXAMPLES")
    print("-" * 70)

    # Show example of each format for small dataset
    example_data = generate_users(3, seed=42)
    example_wrapped = {"users": example_data}

    print("\n=== JSON Format ===")
    print(serialize_json(example_wrapped))

    print("\n=== YAML Format ===")
    print(serialize_yaml(example_wrapped))

    print("\n=== TOON Format ===")
    print(f"users{toon_encode(example_data)}")

    # Save results for graph generation
    import pickle

    results_path = (
        Path(__file__).parent.parent / "graphics-creation" / "exp1_results.pkl"
    )
    results_path.parent.mkdir(exist_ok=True)
    with open(results_path, "wb") as f:
        pickle.dump(results, f)
    print(f"\nResults saved to: {results_path}")

    return results


if __name__ == "__main__":
    run_experiment()
