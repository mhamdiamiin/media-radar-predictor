from app.config import CATEGORY_MAP, SLUG_KEYWORDS


def classify_category(raw_category: str) -> str:
    if not raw_category:
        return "autre"

    # Layer 1 — direct map (known categories)
    if raw_category in CATEGORY_MAP:
        return CATEGORY_MAP[raw_category]

    # Layer 2 — slug keyword matching (unknown future categories)
    slug = raw_category.lower()

    best_category = "autre"
    best_score    = 0

    for category, keywords in SLUG_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in slug)
        if score > best_score:
            best_score    = score
            best_category = category

    return best_category