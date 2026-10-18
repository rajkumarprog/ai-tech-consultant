import argparse
import hashlib
import time
import xml.etree.ElementTree as ET

import httpx

from .db import get_conn, mark_failed, save_page
from .parser import parse_article

SITEMAP = "https://support.brilliantdirectories.com/support/sitemap.xml"
DELAY_SECONDS = 1.0
MAX_TRIES = 3
HEADERS = {"User-Agent": "StudentCapstoneBot/0.1 (educational project)"}


def get_article_urls(client):
    r = client.get(SITEMAP, headers=HEADERS, timeout=30)
    r.raise_for_status()
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    root = ET.fromstring(r.content)
    urls = [u.find("s:loc", ns).text for u in root.findall("s:url", ns)]
    return [u for u in urls if "/articles/" in u]


def fetch(client, url):
    for attempt in range(1, MAX_TRIES + 1):
        try:
            r = client.get(url, headers=HEADERS, timeout=30, follow_redirects=True)
            if r.status_code in (404, 410):
                raise RuntimeError(f"permanent error {r.status_code}")
            r.raise_for_status()
            return r.text
        except RuntimeError:
            raise                                  # permanent: do not retry
        except httpx.HTTPError:
            if attempt == MAX_TRIES:
                raise
            time.sleep(2 ** attempt)               # wait 2s, then 4s


def run(limit):
    conn = get_conn()
    report = {"added_or_updated": 0, "unchanged": 0, "failed": 0}
    with httpx.Client() as client:
        urls = get_article_urls(client)[:limit]
        print(f"Crawling {len(urls)} articles...")
        for url in urls:
            try:
                parsed = parse_article(fetch(client, url), url)
                digest = hashlib.sha256(
                    "".join(c["text"] for c in parsed["chunks"]).encode()).hexdigest()
                old = conn.execute(
                    "SELECT content_hash FROM pages WHERE url=?", (url,)).fetchone()
                if old and old["content_hash"] == digest:
                    report["unchanged"] += 1
                else:
                    save_page(conn, url, parsed["title"], parsed["chunks"], digest)
                    report["added_or_updated"] += 1
            except Exception as e:
                mark_failed(conn, url, str(e))
                report["failed"] += 1
            time.sleep(DELAY_SECONDS)
    print(report)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=15)
    run(ap.parse_args().limit)
