#!/usr/bin/env python3
"""
Point d'entrée unique : exécute le fetch+filtrage des 3 sources (Reddit,
Hacker News, Lobsters), écrit un flux RSS séparé pour chacune, ainsi qu'un
flux "all.xml" qui fusionne les trois.

Chaque source reste un module indépendant dans sources/ — c'est volontaire :
les logiques de fetch/filtrage sont trop différentes d'une plateforme à
l'autre pour être mutualisées sans perdre en lisibilité. Seule
l'infrastructure (génération RSS, écriture de fichier, planification via
GitHub Actions) est commune.

Pensé pour être exécuté périodiquement par GitHub Actions (voir
.github/workflows/update-feeds.yml), mais fonctionne aussi bien en local.
"""

import os

from common import build_feed, write_feed
from sources import hackernews, lobsters, reddit

# Remplace par l'URL GitHub Pages finale une fois le repo créé, ex:
# "https://tonpseudo.github.io/tech-feeds-filter"
PAGES_BASE_URL = "https://numeodev.github.io/tech-feeds-filter"

DOCS_DIR = "docs"

SOURCES = [reddit, hackernews, lobsters]


def run_source(module):
    print(f"→ {module.__name__.split('.')[-1]} ...")
    items = module.fetch()
    print(f"  {len(items)} item(s) retenu(s).")

    self_url = f"{PAGES_BASE_URL}/{module.OUTPUT_FILENAME}"
    fg = build_feed(
        items,
        title=module.FEED_TITLE,
        description=module.FEED_DESCRIPTION,
        link=module.FEED_LINK,
        self_url=self_url,
    )
    output_path = os.path.join(DOCS_DIR, module.OUTPUT_FILENAME)
    write_feed(fg, output_path)
    print(f"  écrit dans {output_path}")
    return items


def build_merged_feed(all_items):
    self_url = f"{PAGES_BASE_URL}/all.xml"
    fg = build_feed(
        all_items,
        title="Tech feeds — Reddit + Hacker News + Lobsters (fusionné)",
        description="Flux combiné des 3 sources filtrées (voir reddit.xml, hackernews.xml, lobsters.xml pour le détail par source).",
        link=PAGES_BASE_URL,
        self_url=self_url,
    )
    output_path = os.path.join(DOCS_DIR, "all.xml")
    write_feed(fg, output_path)
    print(f"→ flux fusionné écrit dans {output_path} ({len(all_items)} item(s))")


def main():
    os.makedirs(DOCS_DIR, exist_ok=True)

    all_items = []
    for module in SOURCES:
        all_items.extend(run_source(module))

    build_merged_feed(all_items)


if __name__ == "__main__":
    main()
