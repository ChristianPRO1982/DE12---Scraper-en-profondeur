# 18 - Livrable - Documentation finale

Partie du brief liee : README, installation locale, lancement du scraper,
chargement PostgreSQL, reprise et livrables.

## Objectif

Cette page sert de point de controle final de la documentation. Elle indique ou
trouver chaque information demandee par le brief et donne un scenario rejouable
depuis une installation locale propre.

## Parcours depuis zero

Depuis la racine du projet :

```bash
cp .env.example .env
uv sync
docker compose up -d
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
uv run scrapy list
```

Ces commandes installent les dependances Python, demarrent PostgreSQL, creent le
schema et verifient que Scrapy charge les spiders.

## Collecte rejouable

Phase 1 :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
```

Sample detaille :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
uv run python -m books_catalog_scraper.validate_exports --sample
```

Full scrape :

```bash
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
uv run python -m books_catalog_scraper.validate_exports --full
```

L'option `-O` rend les exports rejouables en remplacant le fichier cible.

## Chargement PostgreSQL

Chargement depuis un export sample :

```bash
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
```

Chargement depuis l'export final :

```bash
uv run python -m scripts.load_books --input exports/books_details.json
```

Chargement direct pendant le scraping :

```bash
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

La base reste rejouable grace a `ON CONFLICT (upc) DO UPDATE`.

Reprise apres interruption sans revisiter les fiches deja presentes :

```bash
uv run scrapy crawl books_details -a resume_from_db=true -a max_errors=50 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume.json
```

Cette commande sert a la demonstration de reprise. Elle saute les fiches deja
stockees en base et ecrit seulement les fiches restantes dans un export
temporaire.

## Verification PostgreSQL

Requetes de demonstration :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/demo_queries.sql'
```

Apres le chargement final, le total attendu est `1000` livres et les requetes de
doublons ne doivent retourner aucune ligne.

## Qualite

Commandes habituelles :

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
```

La couverture attendue est `100%`.

## Correspondance avec le brief

- Installation depuis zero : `README.md` et `docs/01-preparation-installation.md`.
- Auteur : `README.md`.
- Variables `.env` : `docs/02-preparation-environnement.md`.
- Fonctionnement global : `docs/03-preparation-fonctionnement.md`.
- Qualite : `docs/04-preparation-qualite.md`.
- Reconnaissance : `docs/05-phase-1-reconnaissance.md`.
- Collecte des pages de liste : `docs/06-phase-1-collecteur-pages-liste.md`.
- Collecte des fiches produit : `docs/07-phase-2-collecteur-fiches-produit.md`.
- Temporisation et User-Agent : `docs/08-phase-2-temporisation-user-agent.md`.
- Journal de bord : `docs/09-livrable-journal-de-bord.md`.
- Observations prix et taxe : `docs/10-livrable-observations-prix-taxe.md`.
- Validation des exports : `docs/11-correction-validation-exports.md`.
- Gestion des erreurs : `docs/12-phase-2-gestion-erreurs.md`.
- Stockage PostgreSQL : `docs/13-phase-2-stockage-postgresql.md`.
- Reprise apres interruption : `docs/14-phase-2-reprise-apres-interruption.md`.
- Script de chargement : `docs/15-phase-2-script-chargement.md`.
- Exports : `docs/16-phase-2-exports.md`.
- Requetes de demonstration : `docs/17-livrable-requetes-demonstration.md`.
- Validation finale : `docs/19-livrable-validation-finale.md`.
- Principes de code : `docs/20-livrable-principes-code.md`.

## Validation finale

La validation finale est documentee dans :

- `docs/19-livrable-validation-finale.md`.

Le full scrape final a produit 1 000 fiches dans `exports/books_details.json` et
1 000 livres sont charges dans PostgreSQL.
