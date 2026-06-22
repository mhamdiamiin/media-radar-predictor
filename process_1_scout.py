import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError
from db_config import articles_collection

SITEMAP_URL = "https://www.mosaiquefm.net/fr/sitemap/news.xml"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/124.0.0.0 Safari/537.36"
}

SITEMAP_NS = {
    "ns":    "http://www.sitemaps.org/schemas/sitemap/0.9",
    "image": "http://www.google.com/schemas/sitemap-image/1.1",
}

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
        language   = parts[3] if len(parts) > 3 else None
        category   = parts[4] if len(parts) > 4 else None
        article_id = parts[5] if len(parts) > 5 else None
    except IndexError:
        language = category = article_id = None

    return {
        "language":   language,
        "category":   category,
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

def run_sitemap_scout() -> int:
    print("\n[*] Phase 1 — Fetching sitemap...")

    try:
        response = requests.get(SITEMAP_URL, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[!] Sitemap fetch failed: {e}")
        return 0

    root      = ET.fromstring(response.content)
    url_nodes = root.findall(".//ns:url", SITEMAP_NS)
    print(f"[+] Sitemap loaded — {len(url_nodes)} entries found.")

    new_count = 0

    for node in url_nodes:

        loc       = node.findtext("ns:loc",     namespaces=SITEMAP_NS)
        lastmod   = node.findtext("ns:lastmod", namespaces=SITEMAP_NS)
        image_url = node.findtext(
            "image:image/image:loc", namespaces=SITEMAP_NS
        )

        if not loc:
            continue

        # Skip URLs already in MongoDB — check all 40, never break
        if articles_collection.find_one({"url": loc}):
            continue

        url_meta     = parse_url_meta(loc)
        published_at = parse_published_at(lastmod)

        article_document = {
            "url":        loc,
            "article_id": url_meta["article_id"],
            "status":     "pending",

            "published_at": published_at,
            "image_url":    image_url,
            "language":     url_meta["language"],
            "category":     url_meta["category"],

            
            "title":       None,
            "description": None,
            "tags":        [],

            
            "nlp": {
                "keywords":  [],
                "entities":  [],
                "sentiment": None,
                "embedding": [],
            },

            "tendance": {
                "score":         0.0,
                "velocity":      0.0,
                "cluster_id":    None,
                "is_emerging":   False,
                "score_history": [],
            },

            "scraped_at": None,
            "created_at": datetime.now(timezone.utc),
        }

        try:
            articles_collection.insert_one(article_document)
            print(f"  [+] Staged: [{url_meta['category']}] {url_meta['article_id']}")
            new_count += 1
        except DuplicateKeyError:
            continue

    print(f"[*] Phase 1 done — {new_count} new article(s) staged.\n")
    return new_count


if __name__ == "__main__":
    run_sitemap_scout()