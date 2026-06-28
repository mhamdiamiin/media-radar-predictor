from datetime import datetime, timezone


def parse_url_meta(url: str) -> dict:
    """
    Extract language, category and article_id from the URL.

    URL structure:
      https://www.mosaiquefm.net / fr / actualites-internationales / 1520390 / ...
      index:                        [3]           [4]                    [5]

    Returns dict with language, category, article_id.
    """
    parts = url.rstrip("/").split("/")
    try:
        language = parts[3] if len(parts) > 3 else None
        category = parts[4] if len(parts) > 4 else None
        article_id = parts[5] if len(parts) > 5 else None
    except IndexError:
        language = category = article_id = None

    return {
        "language": language,
        "category": category,
        "article_id": article_id,
    }


def parse_published_at(lastmod: str):
    """
    Convert sitemap <lastmod> string to a UTC datetime object.
    Input:  '2026-06-18T13:09:00+01:00'
    Output: datetime(2026, 6, 18, 12, 9, 0, tzinfo=UTC)
    Returns None if missing or unparseable.
    """
    if not lastmod:
        return None
    try:
        return datetime.fromisoformat(lastmod).astimezone(timezone.utc)
    except ValueError:
        return None


def clean_html(raw_text) -> str:
    import re
    if not raw_text or not isinstance(raw_text, str):
        return ""
    cleaned = re.sub(r"<[^>]+>", "", raw_text)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
