"""Fusion des flux RSS par tag Lobste.rs (pas de filtrage par mots-clés nécessaire)."""

import sys
from datetime import datetime, timezone

import feedparser

TAGS = [
    "devops",
    "security",
    "practices",
    "vcs",
    "distributed",
]

FEED_TITLE = "Lobsters — devops / security / practices / vcs / distributed"
FEED_DESCRIPTION = "Flux fusionné depuis plusieurs tags Lobste.rs."
FEED_LINK = "https://lobste.rs/"
OUTPUT_FILENAME = "lobsters.xml"


def _entry_datetime(entry):
    if getattr(entry, "published_parsed", None):
        return datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
    return datetime.now(timezone.utc)


def fetch():
    """Retourne une liste d'items normalisés (voir common.py), dédupliqués par lien."""
    seen = {}
    for tag in TAGS:
        url = f"https://lobste.rs/t/{tag}.rss"
        parsed = feedparser.parse(url)
        if parsed.bozo and not parsed.entries:
            print(f"⚠️  [lobsters] impossible de charger le tag '{tag}' — ignoré.", file=sys.stderr)
            continue
        for entry in parsed.entries:
            key = getattr(entry, "id", entry.link)
            if key in seen:
                seen[key]["tags"].add(tag)
            else:
                seen[key] = {"entry": entry, "tags": {tag}}

    items = []
    for data in seen.values():
        entry = data["entry"]
        tags_str = ", ".join(sorted(data["tags"]))
        items.append(
            {
                "title": f"[{tags_str}] {entry.title}",
                "link": entry.link,
                "description": getattr(entry, "summary", ""),
                "published": _entry_datetime(entry),
                "guid": getattr(entry, "id", entry.link),
            }
        )
    return items
