"""
TOON (Token-Oriented Object Notation) Encoder

A token-efficient serialization format designed for LLM context windows.
Based on the specification described in the article.

Key features:
- Header-based schemas: column names appear once, not repeated per record
- Explicit length hints: [N] notation tells model how many items to expect
- Minimal delimiters: no quotes unless necessary (containing delimiters)
- Graceful degradation: falls back to YAML-like syntax for non-tabular data
"""

from typing import Any, List, Dict, Union
import re


def needs_escaping(value: str) -> bool:
    """Check if a string value needs escaping due to delimiter characters."""
    return "," in value or "\n" in value or '"' in value


def escape_value(value: str) -> str:
    """Escape a value that contains delimiter characters."""
    if needs_escaping(value):
        # Use double quotes and escape internal quotes
        escaped = value.replace('"', '""')
        return f'"{escaped}"'
    return value


def format_value(value: Any) -> str:
    """Format a single value for TOON output."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return escape_value(value)
    # For complex types, fall back to string representation
    return escape_value(str(value))


def is_tabular(data: List[Dict]) -> bool:
    """Check if a list of dicts has uniform schema (suitable for tabular format)."""
    if not data or not isinstance(data, list):
        return False
    if not all(isinstance(item, dict) for item in data):
        return False

    # Get keys from first item
    first_keys = set(data[0].keys())

    # Check if all items have the same keys
    for item in data[1:]:
        if set(item.keys()) != first_keys:
            return False

    # Check that values are primitives (not nested structures)
    for item in data:
        for value in item.values():
            if isinstance(value, (dict, list)):
                return False

    return True


def encode_tabular(data: List[Dict], name: str = None) -> str:
    """Encode a list of uniform dicts in tabular TOON format."""
    if not data:
        return f"{name}[0]{{}}:\n" if name else "[0]{}:\n"

    # Get keys from first item (preserving order)
    keys = list(data[0].keys())

    # Build header
    count = len(data)
    fields = ",".join(keys)

    if name:
        header = f"{name}[{count}]{{{fields}}}:"
    else:
        header = f"[{count}]{{{fields}}}:"

    # Build rows
    rows = []
    for item in data:
        row_values = [format_value(item.get(key)) for key in keys]
        rows.append(",".join(row_values))

    return header + "\n" + "\n".join(rows)


def encode_nested(data: Any, indent: int = 0) -> str:
    """Encode nested/non-tabular data in YAML-like format."""
    prefix = "  " * indent

    if data is None:
        return "null"
    if isinstance(data, bool):
        return "true" if data else "false"
    if isinstance(data, (int, float)):
        return str(data)
    if isinstance(data, str):
        # For YAML-like format, use quotes if contains special chars
        if ":" in data or "\n" in data or data.startswith(" ") or data.endswith(" "):
            escaped = data.replace('"', '\\"')
            return f'"{escaped}"'
        return data

    if isinstance(data, list):
        if not data:
            return "[]"

        # Check if it's a tabular list
        if is_tabular(data):
            return encode_tabular(data)

        # Otherwise, encode as YAML-like list
        lines = []
        for item in data:
            item_str = encode_nested(item, indent + 1)
            if isinstance(item, (dict, list)) and item:
                lines.append(f"{prefix}- \n{item_str}")
            else:
                lines.append(f"{prefix}- {item_str}")
        return "\n".join(lines)

    if isinstance(data, dict):
        if not data:
            return "{}"

        lines = []
        for key, value in data.items():
            # Check if value is a tabular list
            if isinstance(value, list) and is_tabular(value):
                tabular = encode_tabular(value, name=key)
                lines.append(f"{prefix}{tabular}")
            elif isinstance(value, (dict, list)) and value:
                value_str = encode_nested(value, indent + 1)
                lines.append(f"{prefix}{key}:\n{value_str}")
            else:
                value_str = encode_nested(value, indent)
                lines.append(f"{prefix}{key}: {value_str}")
        return "\n".join(lines)

    return str(data)


def encode(data: Any) -> str:
    """
    Encode data to TOON format.

    For lists of uniform dicts, uses compact tabular format.
    For other structures, uses YAML-like nested format.

    Args:
        data: The data to encode (dict, list, or primitive)

    Returns:
        TOON-formatted string
    """
    if isinstance(data, list) and is_tabular(data):
        return encode_tabular(data)
    return encode_nested(data)


def decode_tabular(text: str) -> List[Dict]:
    """Decode tabular TOON format back to list of dicts."""
    lines = text.strip().split("\n")
    if not lines:
        return []

    # Parse header: name[count]{field1,field2,...}:
    header = lines[0]

    # Extract fields from header
    match = re.match(r"(?:(\w+))?\[(\d+)\]\{([^}]*)\}:", header)
    if not match:
        raise ValueError(f"Invalid TOON header: {header}")

    name, count, fields_str = match.groups()
    expected_count = int(count)
    fields = [f.strip() for f in fields_str.split(",")] if fields_str else []

    # Parse data rows
    result = []
    for line in lines[1:]:
        if not line.strip():
            continue

        # Parse CSV-like values (handling quoted strings)
        values = []
        current = ""
        in_quotes = False

        for char in line:
            if char == '"':
                if in_quotes and len(current) > 0 and current[-1] == '"':
                    current += char
                else:
                    in_quotes = not in_quotes
            elif char == "," and not in_quotes:
                values.append(current)
                current = ""
            else:
                current += char
        values.append(current)

        # Clean up values
        clean_values = []
        for v in values:
            v = v.strip()
            if v.startswith('"') and v.endswith('"'):
                v = v[1:-1].replace('""', '"')
            clean_values.append(v)

        # Create dict
        row_dict = {}
        for i, field in enumerate(fields):
            if i < len(clean_values):
                val = clean_values[i]
                # Try to convert to appropriate type
                if val == "":
                    row_dict[field] = None
                elif val == "true":
                    row_dict[field] = True
                elif val == "false":
                    row_dict[field] = False
                else:
                    try:
                        row_dict[field] = int(val)
                    except ValueError:
                        try:
                            row_dict[field] = float(val)
                        except ValueError:
                            row_dict[field] = val
            else:
                row_dict[field] = None

        result.append(row_dict)

    return result


def decode(text: str) -> Any:
    """
    Decode TOON format back to Python data structure.

    Currently supports tabular format decoding.
    """
    text = text.strip()

    # Check if it's tabular format
    if re.match(r"(?:\w+)?\[\d+\]\{[^}]*\}:", text.split("\n")[0]):
        return decode_tabular(text)

    # For other formats, would need more complex parsing
    raise NotImplementedError("Only tabular TOON decoding is currently supported")


# Convenience alias
dumps = encode
loads = decode
