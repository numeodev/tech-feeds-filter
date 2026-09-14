"""Fetch + filtrage par mots-clés pour Hacker News (via l'API de recherche Algolia)."""

import re
import sys
import time
from datetime import datetime, timedelta, timezone

import requests

KEYWORDS = [
    "postmortem",
    "outage",
    "root cause analysis",
    "incident report",
    "blameless postmortem",
    "bad deploy",
    "bad commit",
    "rollback",
    "revert",
    "broke production",
    "broke prod",
    "took down production",
    "hotfix",
    "git bisect",
    "bad release",
]

LOOKBACK_DAYS = 14
HITS_PER_QUERY = 50

FEED_TITLE = "Hacker News — Incidents & Postmortems (filtré)"
FEED_DESCRIPTION = "Stories Hacker News filtrées par mots-clés via l'API Algolia."
FEED_LINK = "https://news.ycombinator.com/"
OUTPUT_FILENAME = "hackernews.xml"

ALGOLIA_SEARCH_URL = "https://hn.algolia.com/api/v1/search_by_date"


def _pattern():
    escaped = [re.escape(k) for k in KEYWORDS]
    return re.compile(r"(" + "|".join(escaped) + r")", re.IGNORECASE)


def _matches(hit, pattern):
    haystack = " ".join(filter(None, [hit.get("title") or "", hit.get("story_text") or ""]))
    return bool(pattern.search(haystack))


def _fetch_candidates():
    since_ts = int((datetime.now(timezone.utc) - timedelta(days=LOOKBACK_DAYS)).timestamp())
    results = {}
    for kw in KEYWORDS:
        params = {
            "query": kw,
            "tags": "story",
            "numericFilters": f"created_at_i>{since_ts}",
            "hitsPerPage": HITS_PER_QUERY,
        }
        try:
            resp = requests.get(ALGOLIA_SEARCH_URL, params=params, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as exc:
            print(f"⚠️  [hackernews] requête échouée pour '{kw}': {exc}", file=sys.stderr)
            continue
        for hit in resp.json().get("hits", []):
            results[hit["objectID"]] = hit
        time.sleep(0.2)
    return list(results.values())


def fetch():
    """Retourne une liste d'items normalisés (voir common.py)."""
    pattern = _pattern()
    candidates = _fetch_candidates()
    items = []
    for hit in candidates:
        if not _matches(hit, pattern):
            continue
        hn_link = f"https://news.ycombinator.com/item?id={hit['objectID']}"
        story_url = hit.get("url") or hn_link
        points = hit.get("points", 0)
        comments = hit.get("num_comments", 0)
        items.append(
            {
                "title": hit.get("title") or "(sans titre)",
                "link": story_url,
                "description": (
                    f"{points} points, {comments} commentaires — "
                    f"<a href='{hn_link}'>discussion sur Hacker News</a>"
                ),
                "published": datetime.fromtimestamp(hit.get("created_at_i", 0), tz=timezone.utc),
                "guid": hn_link,
            }
        )
    return items
