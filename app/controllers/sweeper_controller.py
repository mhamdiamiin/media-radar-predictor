import json
import time
from datetime import datetime, timezone
from scrapling import Fetcher

from app.config import RATE_LIMIT_DELAY
from app.models.database import articles_collection
from app.utils.parsers import clean_html


class SweeperController:
    def __init__(self):
        self.rate_limit_delay = RATE_LIMIT_DELAY

    def mark_failed(self, url: str, reason: str = ""):
        articles_collection.update_one(
            {"url": url},
            {
                "$set": {
                    "status": "failed",
                    "scraped_at": datetime.now(timezone.utc),
                }
            },
        )
        if reason:
            print(f"  [!] Marked failed — {reason}")

    def run(self):
        print("[*] Phase 2 — Sweeping pending articles...")

        pending = list(articles_collection.find({"status": "pending"}))
        total = len(pending)

        if total == 0:
            print("[-] No pending articles. Pipeline is up to date.\n")
            return

        print(f"[+] {total} pending article(s) to process.\n")

        for index, record in enumerate(pending, start=1):
            url = record["url"]
            print(f"[{index}/{total}] Scraping: {url}")

            try:
                page = Fetcher.get(url)
                script_tags = page.css('script[id="__NEXT_DATA__"]')

                if not script_tags:
                    self.mark_failed(url, "__NEXT_DATA__ script tag not found.")
                    continue

                page_json = json.loads(script_tags[0].text)
                pagedata = page_json["props"]["pageProps"]["pagedata"]
                article = pagedata.get("article", {})
                tags_raw = pagedata.get("tags", [])

                raw_title = article.get("title", "")
                raw_description = article.get("description", "")
                clean_title = clean_html(raw_title)
                clean_description = clean_html(raw_description)

                extracted_tags = []
                for tag in tags_raw:
                    if not isinstance(tag, dict):
                        continue
                    tag_text = tag.get("label", "") or tag.get("name", "")
                    if tag_text:
                        extracted_tags.append(tag_text)

                articles_collection.update_one(
                    {"url": url},
                    {
                        "$set": {
                            "status": "completed",
                            "title": clean_title,
                            "description": clean_description,
                            "tags": extracted_tags,
                            "scraped_at": datetime.now(timezone.utc),
                        }
                    },
                )

                print(f"  [+] OK — '{clean_title[:65]}'")

            except KeyError as e:
                self.mark_failed(url, f"KeyError {e} — pagedata path may have changed.")

            except json.JSONDecodeError as e:
                self.mark_failed(url, f"JSON decode error: {e}")

            except Exception as e:
                self.mark_failed(url, f"Unexpected error: {e}")

            if index < total:
                time.sleep(self.rate_limit_delay)

        n_completed = articles_collection.count_documents({"status": "completed"})
        n_failed = articles_collection.count_documents({"status": "failed"})
        n_pending = articles_collection.count_documents({"status": "pending"})

        print(f"\n[*] Phase 2 done.")
        print(f"    completed : {n_completed}")
        print(f"    failed    : {n_failed}")
        print(f"    pending   : {n_pending}\n")
