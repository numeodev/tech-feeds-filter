# Tech Feeds Filter

Fusionne et filtre Reddit, Hacker News et Lobsters — trois sources, un seul
repo, un seul workflow GitHub Actions, gratuit et sans limite.

## Pourquoi 3 modules et pas 1 script fourre-tout

Les trois plateformes n'ont rien en commun techniquement :

| Source | Méthode | Filtrage |
|---|---|---|
| **Reddit** | flux `.rss` par subreddit | mots-clés (regex) |
| **Hacker News** | API de recherche Algolia | mots-clés (regex) |
| **Lobsters** | flux `.rss` par tag officiel | aucun (tags exacts, pas de faux positif) |

Chaque source vit dans son propre fichier (`sources/reddit.py`,
`sources/hackernews.py`, `sources/lobsters.py`) — modifier les mots-clés
Reddit n'a aucun impact sur Hacker News ou Lobsters. Seule la partie
"infrastructure" est mutualisée : génération RSS (`common.py`),
orchestration (`build_feeds.py`), planification (un seul workflow).

## Sorties générées

Le script écrit **4 fichiers** dans `docs/` :

- `reddit.xml` — Reddit filtré uniquement
- `hackernews.xml` — Hacker News filtré uniquement
- `lobsters.xml` — Lobsters (tags suivis) uniquement
- `all.xml` — les trois fusionnés en un seul flux

Tu peux abonner Blogtrottr à un seul de ces flux (par exemple `all.xml`
pour tout recevoir en un seul type de mail), ou à plusieurs si tu veux les
distinguer.

## Mise en place (une seule fois)

1. **Crée un nouveau repo GitHub** (public, requis pour GitHub Pages
   gratuit), par exemple `tech-feeds-filter`, et pousse-y le contenu de ce
   dossier.

2. **Ouvre `build_feeds.py`** et mets à jour `PAGES_BASE_URL` avec l'URL
   GitHub Pages que ton repo aura, au format :
   `https://TON-PSEUDO-GITHUB.github.io/tech-feeds-filter`
   (sans slash final — champ informatif dans les flux, pas bloquant si
   oublié).

3. **Personnalise chaque source si besoin** : `sources/reddit.py`
   (`SUBREDDITS` / `KEYWORDS`), `sources/hackernews.py` (`KEYWORDS`,
   `LOOKBACK_DAYS`), `sources/lobsters.py` (`TAGS`). Les valeurs actuelles
   reprennent celles déjà définies dans nos échanges précédents.

4. **Active GitHub Pages** : `Settings` → `Pages` → source = branche
   `main`, dossier `/docs`. Sauvegarde.

5. **Lance le workflow une première fois manuellement** : onglet `Actions`
   → `Update filtered tech feeds` → `Run workflow`.

6. Après quelques minutes, tes flux sont disponibles aux URL :
   - `https://TON-PSEUDO.github.io/tech-feeds-filter/reddit.xml`
   - `https://TON-PSEUDO.github.io/tech-feeds-filter/hackernews.xml`
   - `https://TON-PSEUDO.github.io/tech-feeds-filter/lobsters.xml`
   - `https://TON-PSEUDO.github.io/tech-feeds-filter/all.xml`

   Colle celle(s) de ton choix dans Blogtrottr.

Le workflow tourne ensuite seul, toutes les heures, régénère les 4 fichiers
et les commit automatiquement — aucune action de ta part.

## Test en local (optionnel)

```bash
pip install -r requirements.txt
python build_feeds.py
```

## Ajouter une future source

1. Crée `sources/nouvelle_source.py` avec une fonction `fetch()` qui
   retourne une liste d'items normalisés (voir `common.py` pour le format),
   et les constantes `FEED_TITLE`, `FEED_DESCRIPTION`, `FEED_LINK`,
   `OUTPUT_FILENAME`.
2. Ajoute le module à la liste `SOURCES` dans `build_feeds.py`.

Le flux fusionné `all.xml` l'intégrera automatiquement.
