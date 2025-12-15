# TOON (Token-Oriented Object Notation) Performance Test Suite

A comprehensive benchmark suite evaluating **TOON**, a novel token-efficient serialization format designed specifically for LLM context windows. This repository contains the encoder implementation, experimental validation suite, and visualization tools used to demonstrate TOON's performance advantages over JSON and YAML.

## 📋 Overview

TOON is a data serialization format optimized for token efficiency in LLM applications. This repository provides:

- **Reference Implementation**: Complete TOON encoder/decoder in Python
- **Benchmark Suite**: Three rigorous experiments measuring token efficiency, comprehension accuracy, and robustness
- **Visualization Tools**: Scripts to generate publication-quality charts and diagrams
- **Reproducible Results**: All experiments are deterministic and reproducible

## 🎯 Key Features of TOON

- **Header-based schemas**: Column names appear once, not repeated per record
- **Explicit length hints**: `[N]` notation tells the model how many items to expect
- **Minimal delimiters**: No quotes unless necessary (when containing delimiters)
- **Graceful degradation**: Falls back to YAML-like syntax for non-tabular data

### Format Comparison Example

**JSON** (verbose):
```json
{
  "users": [
    {"id": 1, "name": "Alice", "role": "admin"},
    {"id": 2, "name": "Bob", "role": "user"}
  ]
}
```

**TOON** (compact):
```
users[2]{id,name,role}:
1,Alice,admin
2,Bob,user
```

## 📊 Experimental Results

### Experiment 1: Token Consumption at Scale
Tests token efficiency across varying dataset sizes (10-500 records).

**Key Findings:**
- **30-40% token savings** vs JSON at scale
- Savings increase with dataset size
- Consistent overhead reduction

### Experiment 2: Comprehension Validation
Validates GPT-4's ability to extract information from TOON-formatted data.

**Key Findings:**
- **Equivalent or better accuracy** vs JSON (>99% exact match rate)
- **Slightly faster response times** due to reduced input tokens
- Handles specific retrieval, filtering, and aggregation queries

### Experiment 3: Robustness Under Adversarial Conditions
Tests edge cases that expose parsing fragility.

**Test Cases:**
- ✅ Delimiter characters (commas, newlines)
- ✅ Empty/null values
- ✅ Unicode and emoji
- ✅ Long strings (1000+ characters)
- ✅ Deep nesting (4+ levels)

**Key Findings:**
- Perfect round-trip reliability with proper escaping
- Maintains token savings even with edge cases
- LLM comprehension remains robust

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- OpenAI API key (for Experiments 2 & 3)

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/toon-performance-test.git
cd toon-performance-test

# Install dependencies
pip install -r tests/requirements.txt
```

### Running Experiments

**Experiment 1** (Token Consumption - No API Key Required):
```bash
python tests/experiment_1_tokens.py
```

**Experiment 2** (Comprehension - Requires API Key):
```bash
# Create .env file with your API key
echo "API_KEY=your_openai_api_key_here" > .env

# Run with default 100 trials per query (600 total API calls)
python tests/experiment_2_comprehension.py

# Run with fewer trials for faster testing
python tests/experiment_2_comprehension.py --trials 10
```

**Experiment 3** (Robustness - Requires API Key):
```bash
python tests/experiment_3_robustness.py
```

### Using the TOON Encoder

```python
from tests.toon_encoder import encode, decode

# Encode tabular data
data = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"}
]

toon_output = encode(data)
print(toon_output)
# Output:
# [2]{id,name,email}:
# 1,Alice,alice@example.com
# 2,Bob,bob@example.com

# Decode back to Python
decoded = decode(toon_output)
assert decoded == data  # Perfect round-trip
```

## 📈 Generating Visualizations

The repository includes scripts to generate all charts and diagrams:

```bash
cd graphics-creation
python generate_all.py
```

This generates 10 publication-quality graphics in the `graphics/` folder:

1. **Token Breakdown Diagram**: Visual comparison of format structures
2. **Token Counts Bar Chart**: Side-by-side comparison across dataset sizes
3. **Savings Scaling**: Token savings percentage vs dataset size
4. **Accuracy Comparison**: Comprehension test results
5. **Latency Distribution**: Response time analysis
6. **Cost Projection**: Estimated API cost savings
7. **Reliability Cascade**: Edge case test results
8. **Architecture Diagram**: TOON format structure
9. **Decision Flowchart**: When to use TOON
10. **Summary Infographic**: Key metrics overview

## 🏗️ Repository Structure

```
toon-performance-test/
├── tests/                          # Experimental suite
│   ├── toon_encoder.py            # TOON encoder/decoder implementation
│   ├── data_generators.py         # Test data generation utilities
│   ├── experiment_1_tokens.py     # Token consumption experiment
│   ├── experiment_2_comprehension.py  # Comprehension validation
│   ├── experiment_3_robustness.py # Edge case robustness testing
│   └── requirements.txt           # Python dependencies
│
├── graphics-creation/              # Visualization scripts
│   ├── generate_all.py            # Generate all graphics
│   ├── graph_1.py ... graph_10.py # Individual graph generators
│   ├── style.py                   # Consistent styling
│   ├── common.py                  # Shared utilities
│   └── exp*_results.pkl           # Cached experiment results
│
├── graphics/                       # Generated visualizations
│   ├── graph_1_token_breakdown.png
│   ├── graph_2_token_counts.png
│   └── ... (10 total graphics)
│
└── README.md                      # This file
```

## 🔬 Technical Details

### TOON Format Specification

**Tabular Data** (list of uniform dicts):
```
[count]{field1,field2,...}:
value1,value2,...
value1,value2,...
```

**Named Collections**:
```
collection_name[count]{field1,field2}:
value1,value2
```
**Nested Structures**:
Falls back to YAML-like indented format for non-tabular data.

### Token Counting

All experiments use `tiktoken` with the `cl100k_base` encoding (GPT-4 tokenizer) for consistent, reproducible measurements.

### Reproducibility

- Experiments use fixed seeds for deterministic data generation
- Results are cached as pickle files for visualization
- All experiments can be re-run with `--trials` parameter

## 📝 Use Cases

TOON is particularly effective for:

- **Large-scale data analysis**: Product catalogs, user records, log data
- **API responses**: Minimize token costs when sending data to LLMs
- **RAG systems**: Reduce context window pressure for document storage
- **Batch processing**: Process more records per API call

**When NOT to use TOON:**
- Small datasets (<10 records)
- Deeply nested, non-uniform structures
- When human readability is paramount
- Non-LLM contexts where tokens don't matter
