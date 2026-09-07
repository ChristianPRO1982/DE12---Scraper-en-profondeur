# 08 - Phase 2 - Temporisation et User-Agent

Partie du brief liee : phase 2, rythme de crawl, identification du scraper et
respect du site cible.

## Reglages Scrapy

Les reglages sont centralises dans `books_catalog_scraper/settings.py`.

```python
ROBOTSTXT_OBEY = True
USER_AGENT = (
    "DE12-books-scraper/0.1 (+https://github.com/ChristianPRO1982/DE12---Scraper-en-profondeur)"
)
DOWNLOAD_DELAY = 0.5
RANDOMIZE_DOWNLOAD_DELAY = False
CONCURRENT_REQUESTS_PER_DOMAIN = 1
```

## Justification

`ROBOTSTXT_OBEY = True` garde un comportement standard Scrapy. Sur Books to
Scrape, `robots.txt` repond en 404, ce qui signifie qu'aucune directive
technique n'est publiee.

`USER_AGENT` identifie explicitement le projet au lieu d'utiliser un navigateur
factice. C'est plus propre pour un exercice de scraping.

`DOWNLOAD_DELAY = 0.5` ajoute une pause entre les requetes vers le meme domaine.
Le site est un bac a sable prevu pour le scraping, mais le brief demande quand
meme un rythme raisonnable.

`RANDOMIZE_DOWNLOAD_DELAY = False` garde un comportement rejouable : deux
lancements utilisent la meme temporisation.

`CONCURRENT_REQUESTS_PER_DOMAIN = 1` simplifie le raisonnement pour un projet
debutant : une seule requete est envoyee a la fois vers `books.toscrape.com`.
L'ordre des traitements est plus previsible et la charge envoyee au site reste
faible.

## Commandes rejouables

Collecte echantillon :

```bash
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
```

Collecte complete :

```bash
uv run scrapy crawl books_details -O exports/books_details.json
```

L'option `-O` remplace l'export precedent. Les commandes peuvent donc etre
relancees sans suppression manuelle des fichiers.

## Verification

Les reglages sont verifies par les tests :

```bash
uv run pytest -q tests/test_settings.py
```

La chaine qualite complete reste :

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
```
