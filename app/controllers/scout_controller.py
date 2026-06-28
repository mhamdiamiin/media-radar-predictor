import xml.etree.ElementTree as ET
import requests
from datetime import datetime, timezone
from pymongo.errors import DuplicateKeyError

from app.config import SITEMAP_URL, HEADERS, SITEMAP_NS, REQUEST_TIMEOUT
from app.models.database import articles_collection
from app.utils.parsers import parse_url_meta, parse_published_at


class ScoutController:
    def __init__(self):
        self.sitemap_url = SITEMAP_URL
        self.headers = HEADERS
        self.ns = SITEMAP_NS

    def run(self) -> int:
        print("\n[*] Phase 1 — Fetching sitemap...")

        try:
            response = requests.get(
                self.sitemap_url,
                headers=self.headers,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"[!] Sitemap fetch failed: {e}")
            return 0

        root = ET.fromstring(response.content)
        url_nodes = root.findall(".//ns:url", self.ns)
        print(f"[+] Sitemap loaded — {len(url_nodes)} entries found.")

        new_count = 0

        for node in url_nodes:
            loc = node.findtext("ns:loc", namespaces=self.ns)
            lastmod = node.findtext("ns:lastmod", namespaces=self.ns)
            image_url = node.findtext(
                "image:image/image:loc", namespaces=self.ns
            )

            if not loc:
                continue

            if articles_collection.find_one({"url": loc}):
                continue

            url_meta = parse_url_meta(loc)
            published_at = parse_published_at(lastmod)

            article_document = {
                "url": loc,
                "article_id": url_meta["article_id"],
                "status": "pending",
                "published_at": published_at,
                "image_url": image_url,
                "language": url_meta["language"],
                "category": url_meta["category"],
                "title": None,
                "description": None,
                "tags": [],
                "nlp": {
                    "keywords": [],
                    "entities": [],
                    "sentiment": None,
                    "embedding": [],
                },
                "tendance": {
                    "score": 0.0,
                    "velocity": 0.0,
                    "cluster_id": None,
                    "is_emerging": False,
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
