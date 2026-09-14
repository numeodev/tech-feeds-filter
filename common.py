"""
Fonctions partagées par les 3 sources (Reddit, Hacker News, Lobsters) pour
générer un flux RSS à partir d'une liste d'items normalisés.

Chaque source expose ses propres items sous la forme d'un dict :
    {
        "title": str,
        "link": str,
        "description": str (peut contenir du HTML simple),
        "published": datetime (timezone-aware),
        "guid": str,
    }
"""

from feedgen.feed import FeedGenerator


def build_feed(items, title, description, link, self_url, max_items=200):
    """Construit un objet FeedGenerator à partir d'une liste d'items normalisés."""
    fg = FeedGenerator()
    fg.title(title)
    fg.link(href=link, rel="alternate")
    fg.link(href=self_url, rel="self")
    fg.description(description)
    fg.language("en")

    items_sorted = sorted(items, key=lambda i: i["published"], reverse=True)[:max_items]

    # feedgen ajoute les items dans l'ordre inverse de l'appel -> on itère à l'envers
    for item in reversed(items_sorted):
        fe = fg.add_entry()
        fe.id(item["guid"])
        fe.title(item["title"])
        fe.link(href=item["link"])
        fe.description(item["description"])
        fe.pubDate(item["published"])

    return fg


def write_feed(fg, output_path):
    fg.rss_file(output_path, pretty=True)
