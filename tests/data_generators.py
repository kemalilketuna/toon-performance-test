"""
Data generators for TOON experiments.

Provides consistent, reproducible test data generation with fixed random seeds.
"""

import random
from typing import List, Dict, Any


# Common first and last names for realistic data
FIRST_NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "Diana",
    "Edward",
    "Fiona",
    "George",
    "Hannah",
    "Isaac",
    "Julia",
    "Kevin",
    "Laura",
    "Michael",
    "Nina",
    "Oscar",
    "Paula",
    "Quinn",
    "Rachel",
    "Samuel",
    "Tina",
    "Ulysses",
    "Victoria",
    "Walter",
    "Xena",
    "Yusuf",
    "Zara",
    "Adrian",
    "Bella",
    "Carlos",
    "Daphne",
    "Ethan",
    "Freya",
]

LAST_NAMES = [
    "Smith",
    "Johnson",
    "Williams",
    "Brown",
    "Jones",
    "Garcia",
    "Miller",
    "Davis",
    "Rodriguez",
    "Martinez",
    "Hernandez",
    "Lopez",
    "Gonzalez",
    "Wilson",
    "Anderson",
    "Thomas",
    "Taylor",
    "Moore",
    "Jackson",
    "Martin",
    "Lee",
    "Perez",
    "Thompson",
    "White",
    "Harris",
    "Sanchez",
    "Clark",
    "Ramirez",
    "Lewis",
    "Robinson",
    "Walker",
]

ROLES = ["admin", "user", "moderator", "guest", "editor"]

CATEGORIES = [
    "Electronics",
    "Clothing",
    "Home & Garden",
    "Sports",
    "Books",
    "Toys",
    "Food",
    "Health",
]

PRODUCT_ADJECTIVES = [
    "Premium",
    "Basic",
    "Pro",
    "Ultra",
    "Mini",
    "Mega",
    "Smart",
    "Classic",
]
PRODUCT_NOUNS = ["Widget", "Gadget", "Device", "Tool", "System", "Kit", "Set", "Pack"]


def generate_name(rng: random.Random) -> str:
    """Generate a realistic full name (~12 characters average)."""
    first = rng.choice(FIRST_NAMES)
    last = rng.choice(LAST_NAMES)
    return f"{first} {last}"


def generate_email(name: str, rng: random.Random) -> str:
    """Generate email from name."""
    # Convert name to email format
    parts = name.lower().split()
    domains = ["example.com", "test.org", "demo.net", "sample.io"]
    domain = rng.choice(domains)

    formats = [
        f"{parts[0]}.{parts[1]}@{domain}",
        f"{parts[0][0]}{parts[1]}@{domain}",
        f"{parts[0]}_{parts[1]}@{domain}",
    ]
    return rng.choice(formats)


def generate_users(n: int, seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generate n user records with consistent structure.

    Fields: id, name, email, role, active
    """
    rng = random.Random(seed)
    users = []

    for i in range(1, n + 1):
        name = generate_name(rng)
        users.append(
            {
                "id": i,
                "name": name,
                "email": generate_email(name, rng),
                "role": rng.choice(ROLES),
                "active": rng.choice([True, False]),
            }
        )

    return users


def generate_products(n: int, seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generate n product records with consistent structure.

    Fields: id, name, category, price, stock
    """
    rng = random.Random(seed)
    products = []

    for i in range(1, n + 1):
        adj = rng.choice(PRODUCT_ADJECTIVES)
        noun = rng.choice(PRODUCT_NOUNS)
        name = f"{adj} {noun} {rng.randint(100, 999)}"

        products.append(
            {
                "id": i,
                "name": name,
                "category": rng.choice(CATEGORIES),
                "price": round(rng.uniform(9.99, 999.99), 2),
                "stock": rng.randint(0, 500),
            }
        )

    return products


def generate_edge_case_data(seed: int = 42) -> Dict[str, List[Dict]]:
    """
    Generate edge case datasets for robustness testing.

    Returns dict with different edge case categories.
    """
    rng = random.Random(seed)

    # 1. Strings with delimiter characters
    delimiter_strings = [
        {"id": 1, "name": "O'Brien, James", "note": "Has comma, and apostrophe"},
        {"id": 2, "name": "Smith\nJones", "note": "Has newline"},
        {"id": 3, "name": 'Say "Hello"', "note": "Has quotes"},
        {"id": 4, "name": "Normal Name", "note": "No special chars"},
    ]

    # 2. Empty/null values
    empty_values = [
        {"id": 1, "name": "Complete", "email": "test@test.com", "bio": "Full record"},
        {"id": 2, "name": "Missing Email", "email": None, "bio": "No email"},
        {"id": 3, "name": "", "email": "empty@test.com", "bio": "Empty name"},
        {"id": 4, "name": "No Bio", "email": "nobio@test.com", "bio": None},
    ]

    # 3. Unicode and emoji
    unicode_data = [
        {"id": 1, "name": "José García", "status": "Active"},
        {"id": 2, "name": "田中太郎", "status": "日本語"},
        {"id": 3, "name": "Müller", "status": "Ü is for Über"},
        {"id": 4, "name": "User 🎉", "status": "Has emoji 🚀✨"},
    ]

    # 4. Long strings
    long_strings = [
        {"id": 1, "title": "Short", "content": "Brief content"},
        {
            "id": 2,
            "title": "Medium Length Title Here",
            "content": "A" * 200,  # 200 char string
        },
        {
            "id": 3,
            "title": "Long Content Document",
            "content": "B" * 1000,  # 1000 char string
        },
    ]

    # 5. Deeply nested structures (for fallback testing)
    deep_nested = {
        "level1": {
            "level2": {"level3": {"level4": {"level5": {"value": "deeply nested"}}}}
        }
    }

    return {
        "delimiter_strings": delimiter_strings,
        "empty_values": empty_values,
        "unicode_data": unicode_data,
        "long_strings": long_strings,
        "deep_nested": deep_nested,
    }


def generate_simple_users(n: int, seed: int = 42) -> List[Dict[str, Any]]:
    """
    Generate simple user records matching article example format.

    Fields: id, name, role (3 fields, simpler than full users)
    """
    rng = random.Random(seed)
    users = []

    for i in range(1, n + 1):
        users.append(
            {"id": i, "name": rng.choice(FIRST_NAMES), "role": rng.choice(ROLES)}
        )

    return users


if __name__ == "__main__":
    # Demo the generators
    print("=== Sample Users (5) ===")
    for user in generate_users(5):
        print(user)

    print("\n=== Sample Products (3) ===")
    for product in generate_products(3):
        print(product)

    print("\n=== Edge Cases ===")
    edge_cases = generate_edge_case_data()
    for category, data in edge_cases.items():
        print(f"\n{category}:")
        print(data)
