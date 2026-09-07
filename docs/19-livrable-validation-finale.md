# 19 - Livrable - Validation finale

Partie du brief liee : validation finale, 1 000 livres en base PostgreSQL,
exports complets et absence de doublons.

## Objectif

Valider le projet de bout en bout avec des commandes rejouables :

- demarrage PostgreSQL ;
- creation ou mise a jour du schema ;
- full scrape ;
- export JSON final ;
- chargement PostgreSQL ;
- validation automatique des exports ;
- requetes SQL de demonstration ;
- controle qualite Python.

## Commandes executees

Preparation :

```bash
uv sync
docker compose up -d
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
uv run scrapy list
```

Full scrape avec export et stockage :

```bash
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

Validation de l'export final :

```bash
uv run python -m books_catalog_scraper.validate_exports --full
```

Rejeu du chargement final depuis l'export :

```bash
uv run python -m scripts.load_books --input exports/books_details.json
```

Requetes de demonstration :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/demo_queries.sql'
```

## Resultats Scrapy

Resultat du full scrape :

- 50 pages de liste parcourues ;
- 1 000 fiches programmees ;
- 1 000 livres exportes ;
- 1 000 livres sauvegardes dans PostgreSQL ;
- 0 carte ignoree ;
- 0 doublon URL ignore ;
- 0 echec ;
- export final ecrit dans `exports/books_details.json`.

Le site ne publie pas de `robots.txt` : Scrapy a controle l'URL et a recu une
reponse HTTP 404, ce qui correspond aux observations de reconnaissance.

## Resultats validation export

Le validateur `--full` confirme :

- 1 000 livres dans l'export de phase 1 ;
- 1 000 URLs phase 1 uniques ;
- 1 000 fiches detaillees ;
- 1 000 UPC uniques ;
- 1 000 URLs detaillees uniques ;
- 0 URL manquante ;
- 0 URL supplementaire ;
- 0 rating invalide ;
- 0 stock invalide ;
- 0 nombre d'avis invalide ;
- 0 categorie absente ;
- 2 descriptions absentes ;
- 0 difference de prix observee ;
- 0 erreur bloquante.

Les 2 descriptions absentes ne sont pas bloquantes : le contrat accepte
`description` en chaine de caracteres ou `null`.

## Resultats PostgreSQL

Controles directs :

```sql
SELECT COUNT(*) FROM books;
```

Resultat : `1000`.

```sql
SELECT COUNT(*)
FROM (
    SELECT upc
    FROM books
    GROUP BY upc
    HAVING COUNT(*) > 1
) AS duplicates;
```

Resultat : `0`.

```sql
SELECT COUNT(*)
FROM (
    SELECT product_url
    FROM books
    GROUP BY product_url
    HAVING COUNT(*) > 1
) AS duplicates;
```

Resultat : `0`.

Le script `scripts.load_books` a ete relance sur `exports/books_details.json` et
a recharge 1 000 livres par upsert sans creer de doublons.

## Rejouabilite

Les commandes restent rejouables :

- `db/schema.sql` utilise `CREATE TABLE IF NOT EXISTS`,
  `CREATE INDEX IF NOT EXISTS` et `CREATE OR REPLACE VIEW` ;
- Scrapy ecrit les exports avec `-O`, donc le fichier cible est remplace ;
- PostgreSQL utilise `ON CONFLICT (upc) DO UPDATE` ;
- le script de chargement reutilise les memes upserts que le pipeline.

## Qualite

Commandes de controle :

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
```

La couverture attendue reste `100%`.
