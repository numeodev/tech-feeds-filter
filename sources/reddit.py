"""Fetch + filtrage par mots-clés pour Reddit (via les flux .rss par subreddit)."""

import re
import sys
from datetime import datetime, timezone

import feedparser

SUBREDDITS = [
    "sre",
    "devops",
    "ExperiencedDevs",
    "EngineeringManagers",
    "AskNetsec",
    "kubernetes",
]

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

FEED_TITLE = "Reddit — Incidents & Postmortems (filtré)"
FEED_DESCRIPTION = "Flux fusionné et filtré par mots-clés depuis plusieurs subreddits."
FEED_LINK = "https://www.reddit.com/"
OUTPUT_FILENAME = "reddit.xml"


def _pattern():
    escaped = [re.escape(k) for k in KEYWORDS]
    return re.compile(r"(" + "|".join(escaped) + r")", re.IGNORECASE)


def _matches(entry, pattern):
    haystack = " ".join(filter(None, [getattr(entry, "title", ""), getattr(entry, "summary", "")]))
    return bool(pattern.search(haystack))


def _entry_datetime(entry):
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def fetch():
    """Retourne une liste d'items normalisés (voir common.py)."""
    pattern = _pattern()
    items = []
    for sub in SUBREDDITS:
        url = f"https://www.reddit.com/r/{sub}/.rss"
        parsed = feedparser.parse(url)
        if parsed.bozo and not parsed.entries:
            print(f"⚠️  [reddit] impossible de charger r/{sub} — ignoré.", file=sys.stderr)
            continue
        for entry in parsed.entries:
            if not _matches(entry, pattern):
                continue
            items.append(
                {
                    "title": f"[r/{sub}] {entry.title}",
                    "link": entry.link,
                    "description": getattr(entry, "summary", ""),
                    "published": _entry_datetime(entry),
                    "guid": getattr(entry, "id", entry.link),
                }
            )
    return items
