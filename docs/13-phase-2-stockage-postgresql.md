# 13 - Phase 2 - Stockage PostgreSQL

Partie du brief liee : chargement des livres dans PostgreSQL, choix de cle et
absence de doublons lors d'une seconde execution.

## Principe

Le stockage PostgreSQL est gere par un pipeline Scrapy optionnel :

```text
books_catalog_scraper.pipelines.PostgresPipeline
```

Le pipeline est declare dans les reglages Scrapy, mais il est desactive par
defaut :

```python
POSTGRES_ENABLED = False
```

Cela permet de continuer a produire les exports JSON sans avoir besoin de
PostgreSQL.

## Preparation de la base

Demarrer PostgreSQL :

```bash
docker compose up -d
```

Creer ou mettre a jour le schema :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
```

Le schema contient :

- `categories` ;
- `books` ;
- les vues `books_catalog`, `books_stock_alerts` et `books_best_rated`.

## Commandes rejouables

Charger un echantillon en base :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -s POSTGRES_ENABLED=true -O exports/books_details_sample.json
```

Charger toute la collecte en base :

```bash
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

L'option `-O` remplace l'export JSON precedent.

Le stockage en base est rejouable grace a `ON CONFLICT (upc) DO UPDATE`.

## Cle de reprise

La cle metier retenue est `books.upc`.

Le titre n'est pas utilise comme cle, car le catalogue peut contenir plusieurs
produits avec un meme titre.

## Fonctionnement du pipeline

Pour chaque item detaille :

- inserer ou mettre a jour la categorie par son nom ;
- recuperer `categories.id` ;
- inserer ou mettre a jour le livre dans `books` ;
- faire un `commit` apres l'item.

Le `commit` apres chaque item rend une interruption moins problematique : les
livres deja traites restent en base.

## Variables d'environnement

Le pipeline lit les variables PostgreSQL depuis l'environnement ou depuis le
fichier `.env` :

- `POSTGRES_DB` ;
- `POSTGRES_USER` ;
- `POSTGRES_PASSWORD` ;
- `POSTGRES_HOST` ;
- `POSTGRES_PORT`.

## Verification SQL

Compter les livres :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT COUNT(*) FROM books;"'
```

Verifier les doublons UPC :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT upc, COUNT(*) FROM books GROUP BY upc HAVING COUNT(*) > 1;"'
```

Lire le catalogue :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -c "SELECT upc, title, category, stock_quantity, rating FROM books_catalog ORDER BY title LIMIT 10;"'
```

Lancer toutes les requetes de demonstration :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/demo_queries.sql'
```

## Validation realisee

Validation echantillon lancee le 2026-09-07 :

```bash
uv run scrapy crawl books_details -a limit=3 -a max_errors=5 -s POSTGRES_ENABLED=true -O /tmp/books_details_postgres_sample.json
```

Resultat Scrapy :

- 3 fiches programmees ;
- 3 livres exportes ;
- 3 livres sauvegardes dans PostgreSQL ;
- 0 echec.

Verification PostgreSQL apres relance :

- `SELECT COUNT(*) FROM books;` : 3 ;
- doublons UPC : 0 ;
- `SELECT COUNT(*) FROM categories;` : 3.

## Verification code

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
```
