from app.config import TREND_THRESHOLD
from app.utils.google_trends import get_trends_score


def sentiment_weight(sentiment: dict) -> float:
    if not sentiment:
        return 0.1

    label = sentiment.get("label", "neutral")
    score = sentiment.get("score", 0.0)

    if label == "neutral":
        return 0.2    # was 0.0 → now small baseline

    return round(score, 4)


def entity_weight(entities: list) -> float:
    if not entities:
        return 0.1

    type_weights = {
        "GPE": 0.9,
        "ORG": 0.7,
        "PER": 0.6,
        "LOC": 0.5,
    }

    scores      = [type_weights.get(e.get("label", ""), 0.3) for e in entities]
    avg         = sum(scores) / len(scores)
    count_bonus = min(len(entities) * 0.05, 0.2)

    # penalty if no PER or ORG entities — likely a schedule/list article
    types = [e.get("label", "") for e in entities]
    has_person_or_org = any(t in ("PER", "ORG") for t in types)

    if not has_person_or_org:
        avg = avg * 0.6    # reduce weight if only locations mentioned

    return round(min(avg + count_bonus, 1.0), 4)


def description_weight(description: str) -> float:
    length = len(description) if description else 0

    if length < 300:
        return 0.0
    elif length < 500:
        return 0.15
    elif length < 800:
        return 0.45
    elif length < 1500:
        return 0.70
    else:
        return 0.90


def calculate_initial_score(sentiment:   dict,entities:    list,description: str  = "",keywords:    list = [],use_trends:  bool = True, published_at = None) -> float:
    s_weight = sentiment_weight(sentiment)
    e_weight = entity_weight(entities)
    d_weight = description_weight(description)
    

    if use_trends and keywords:
        g_weight = get_trends_score(keywords, entities, published_at)
    else:
        g_weight = 0.5   # neutral if trends disabled

    # rebalanced weights — trends adds a new external signal
    score = (s_weight * 0.20) + \
            (e_weight * 0.25) + \
            (d_weight * 0.25) + \
            (g_weight * 0.30)

    return round(score, 4)


def determine_label(score: float, cluster_label: str) -> str:
    """
    Determines the final label for an article.

    Rules:
    - mimic   → already labeled by clustering, skip scoring
    - revisit → run scoring but with a historical boost
    - None    → new topic, run scoring normally
    """
    if cluster_label == "mimic":
        return "mimic"

    if cluster_label == "revisit":
        boosted_score = min(score + 0.15, 1.0)
        if boosted_score >= TREND_THRESHOLD:
            return "trend"
        return "fiddling"

    if score >= TREND_THRESHOLD:
        return "trend"

    return "fiddling"


def update_confidence(current_score: float, cluster_size: int, description: str = "") -> float:
    if cluster_size <= 1:
        return current_score

    # don't boost short/routine articles
    if len(description) < 400:
        return current_score

    # only boost if article already has a meaningful initial score
    if current_score < 0.50:
        return current_score

    boost = min((cluster_size - 1) * 0.02, 0.15)
    return round(min(current_score + boost, 1.0), 4)