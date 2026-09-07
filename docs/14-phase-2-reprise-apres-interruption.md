# 14 - Phase 2 - Reprise apres interruption

Partie du brief liee : reprise d'un scraping interrompu et absence de doublons
apres une seconde execution.

## Principe

La reprise repose sur PostgreSQL :

- chaque livre detaille est ecrit en base des son extraction ;
- un `commit` est fait apres chaque item ;
- la cle metier est `books.upc` ;
- l'insertion utilise `ON CONFLICT (upc) DO UPDATE`.

Si le scraper est interrompu, les livres deja sauvegardes restent donc en base.

Au lancement suivant, les memes UPC sont mis a jour au lieu d'etre inseres une
seconde fois.

## Commande echantillon rejouable

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -s POSTGRES_ENABLED=true -O exports/books_details_sample.json
```

Cette commande peut etre relancee plusieurs fois.

L'export JSON est remplace par `-O`.

Les lignes PostgreSQL existantes sont mises a jour par l'upsert.

## Scenario de demonstration

Preparer la base :

```bash
docker compose up -d
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
```

Lancer une premiere collecte partielle :

```bash
uv run scrapy crawl books_details -a limit=3 -a max_errors=5 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume_sample.json
```

Relancer exactement la meme commande :

```bash
uv run scrapy crawl books_details -a limit=3 -a max_errors=5 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume_sample.json
```

Verifier le nombre de livres :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT COUNT(*) FROM books;"'
```

Verifier les doublons UPC :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT COUNT(*) FROM (SELECT upc FROM books GROUP BY upc HAVING COUNT(*) > 1) AS duplicates;"'
```

Resultat attendu :

- le nombre de livres ne double pas ;
- le nombre de doublons UPC reste `0`.

## Validation realisee

Validation realisee le 2026-09-07 avec la commande :

```bash
uv run scrapy crawl books_details -a limit=3 -a max_errors=5 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume_sample.json
```

La commande a ete relancee.

Resultat apres relance :

- `SELECT COUNT(*) FROM books;` : 3 ;
- doublons UPC : 0 ;
- doublons URL produit : 0.

## Interruption manuelle

Pour demontrer une interruption sur une collecte plus longue :

```bash
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

Interrompre avec `Ctrl+C`, puis relancer la meme commande.

Les livres deja sauvegardes sont mis a jour grace a l'UPC.

## Limite assumee

Le crawler reparcourt les pages depuis le debut.

La reprise garantit l'absence de doublons et la conservation des livres deja
sauvegardes, mais elle ne saute pas encore les fiches deja presentes en base.

Cette approche reste simple, explicite et suffisante pour le brief.
