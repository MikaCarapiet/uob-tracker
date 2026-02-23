"""
Auto-categorize transactions based on merchant keyword mapping.
Returns None if no confident match — triggers Telegram prompt.
"""

from typing import Optional

CATEGORIES: dict[str, list[str]] = {
    "Food & Drink": [
        "mcdonalds", "mcdonald", "burger king", "kfc", "subway", "jollibee",
        "starbucks", "ya kun", "toast box", "kopitiam", "hawker", "foodcourt",
        "the coffee bean", "old chang kee", "bengawan", "swensens",
        "pizza", "sushi", "ramen", "pho", "noodle", "restaurant", "cafe",
        "grabfood", "foodpanda", "deliveroo",
    ],
    "Transport": [
        "grab", "gojek", "comfort", "citycab", "smrt", "transit link",
        "ez-link", "ez link", "nets", "taxi", "bus", "mrt", "lta",
        "grab*taxi", "grab*car",
    ],
    "Groceries": [
        "fairprice", "ntuc", "sheng siong", "cold storage", "giant",
        "don don donki", "donki", "marketplace", "jasons",
    ],
    "Shopping": [
        "uniqlo", "h&m", "zara", "cotton on", "charles & keith",
        "lazada", "shopee", "amazon", "zalora", "nike", "adidas",
        "decathlon", "ikea",
    ],
    "Entertainment": [
        "netflix", "spotify", "apple", "google play", "steam", "playstation",
        "cathay", "gv", "golden village", "shaw", "cinema",
        "youtube premium",
    ],
    "Bills & Utilities": [
        "singtel", "starhub", "m1", "circles", "simba", "tpg",
        "sp group", "sp services", "puc", "town council",
        "insurance", "prudential", "aia", "great eastern", "ntuc income",
        "mediashield",
    ],
    "Health & Fitness": [
        "guardian", "watsons", "unity", "pharmacy", "clinic",
        "hospital", "polyclinic", "dental", "gym", "fitness",
        "anytime fitness", "pure fitness", "crossfit",
    ],
    "Travel": [
        "airline", "airasia", "singapore airlines", "sia", "scoot",
        "jetstar", "booking.com", "agoda", "airbnb", "hotel",
        "changi", "airport",
    ],
    "El Matador": [
        "el matador", "matador", "sous vide",
    ],
}


def auto_categorize(description: str) -> Optional[str]:
    """
    Returns a category string if confident, else None.
    """
    desc_lower = description.lower()
    for category, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in desc_lower:
                return category
    return None
