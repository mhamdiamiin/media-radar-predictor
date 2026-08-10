import time
from pytrends.request import TrendReq
from app.config import GOOGLE_TRENDS_TIMEFRAME, GOOGLE_TRENDS_GEO

_pytrends = None

def get_pytrends():
    global _pytrends
    if _pytrends is None:
        _pytrends = TrendReq(
            hl="fr-TN",
            tz=60,        # Tunisia UTC+1 
            timeout=(10, 25),
            retries=2,
            backoff_factor=0.5
        )
    return _pytrends


def build_query(keywords: list, entities: list) -> str:
    """
    Builds the best possible search query from keywords and entities.
    Prioritizes entity names (more specific) over generic keywords.
    Takes max 2 terms to keep query focused.
    """
    # extract entity texts — more specific than keywords
    entity_texts = [e["text"] for e in entities] if entities else []

    # combine entities first then keywords
    all_terms = entity_texts + keywords

    # clean and deduplicate
    seen  = set()
    clean = []
    for term in all_terms:
        t = term.strip().lower()
        if t and t not in seen and len(t) > 2:
            seen.add(t)
            clean.append(term.strip())

    # take top 2 terms — Google Trends works better with focused queries
    top_terms = clean[:2]

    return " ".join(top_terms) if top_terms else ""


def get_trends_score(keywords: list, entities: list, published_at=None) -> float:
    try:
        query = build_query(keywords, entities)
        if not query:
            return 0.5

        pytrends = get_pytrends()

        # use publication date context if available
        if published_at:
            from datetime import datetime, timezone, timedelta
            if published_at.tzinfo is None:
                published_at = published_at.replace(tzinfo=timezone.utc)
            
            days_ago = (datetime.now(timezone.utc) - published_at).days
            
            if days_ago <= 1:
                timeframe = "now 1-d"      # very fresh → last 24h
            elif days_ago <= 7:
                timeframe = "now 7-d"      # this week → last 7 days
            elif days_ago <= 30:
                timeframe = "today 1-m"    # this month → last 30 days
            else:
                return 0.5                 # too old → pytrends useless → neutral
        else:
            timeframe = GOOGLE_TRENDS_TIMEFRAME

        pytrends.build_payload(
            kw_list=[query],
            cat=0,
            timeframe=timeframe,
            geo=GOOGLE_TRENDS_GEO
        )

        time.sleep(2)

        data = pytrends.interest_over_time()

        if data.empty:
            return 0.5

        avg_interest = data[query].mean()
        return round(avg_interest / 100, 4)

    except Exception as e:
        if "429" in str(e) or "Too Many Requests" in str(e):
            print(f"[trends] Rate limited — waiting 30 seconds...")
            time.sleep(30)
            try:
                data = pytrends.interest_over_time()
                if not data.empty:
                    return round(data[query].mean() / 100, 4)
            except:
                pass
        print(f"[trends] Error: {e} — using neutral score 0.5")
        return 0.5