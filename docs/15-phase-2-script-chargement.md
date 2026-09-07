# 15 - Phase 2 - Script de chargement

Partie du brief liee : script de chargement separe et chargement PostgreSQL
rejouable.

## Objectif

Le script `scripts.load_books` charge un export JSON detaille dans PostgreSQL
sans relancer le scraping.

Il reutilise les memes regles que le pipeline Scrapy :

- insertion ou mise a jour de la categorie ;
- insertion ou mise a jour du livre ;
- cle metier `books.upc` ;
- `ON CONFLICT (upc) DO UPDATE` ;
- `commit` apres chaque livre.

## Commande echantillon

```bash
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
```

`--allow-sample` autorise un fichier contenant moins de 1 000 fiches.

## Commande finale

```bash
uv run python -m scripts.load_books --input exports/books_details.json
```

Sans `--allow-sample`, le script exige 1 000 fiches detaillees valides avant de
charger.

## Rejouabilite

Le script est rejouable :

- il valide l'export avant chargement ;
- il utilise l'upsert PostgreSQL ;
- une seconde execution met a jour les lignes existantes ;
- elle ne cree pas de doublons UPC.

## Preparation

```bash
docker compose up -d
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
```

## Sequence recommandee

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
uv run python -m books_catalog_scraper.validate_exports --sample
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
```

Pour le livrable final :

```bash
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
uv run python -m books_catalog_scraper.validate_exports --full
uv run python -m scripts.load_books --input exports/books_details.json
```

## Verification

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT COUNT(*) FROM books;"'
```

Verifier les doublons :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT COUNT(*) FROM (SELECT upc FROM books GROUP BY upc HAVING COUNT(*) > 1) AS duplicates;"'
```

## Validation realisee

Validation realisee le 2026-09-07 :

```bash
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
```

La commande a ete relancee.

Resultat apres relance :

- 20 livres en base ;
- 0 doublon UPC.

## Tests

```bash
uv run pytest -q tests/test_load_books.py
```
