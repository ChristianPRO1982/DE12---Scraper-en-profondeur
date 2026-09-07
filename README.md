# Scraper en profondeur - Books to Scrape

Projet d'ecole pour apprendre a scraper un catalogue en profondeur avec
Scrapy, PostgreSQL, Docker et UV.

Le site cible est le bac a sable legal d'entrainement :
<https://books.toscrape.com/>

Depot du projet :
<https://github.com/ChristianPRO1982/DE12---Scraper-en-profondeur>

## Objectif

Le projet doit collecter les livres du catalogue, visiter les fiches produit,
recuperer les informations absentes des pages de liste, puis charger le resultat
dans PostgreSQL.

Le developpement suivra le brief fourni dans [brief/brief.md](brief/brief.md).

## Technologies

- Python gere avec UV
- Scrapy pour le scraping
- PostgreSQL pour le stockage
- Docker Compose pour lancer la base en local
- Pas de Node.js

## Installation locale

Prerequis attendus :

- Python 3.11 ou plus recent
- UV
- Docker avec Docker Compose

Configurer l'environnement :

```bash
cp .env.example .env
```

Installer les dependances Python :

```bash
uv sync
```

Lancer PostgreSQL :

```bash
docker compose up -d
```

Creer les tables :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
```

Verifier que le projet Scrapy est visible :

```bash
uv run scrapy list
```

La commande doit lister les spiders `books_list` et `books_details`.

## Parcours complet rejouable

Sequence courte depuis un projet configure :

```bash
docker compose up -d
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
uv run scrapy crawl books_list -O exports/books_list.json
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
uv run python -m books_catalog_scraper.validate_exports --sample
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/demo_queries.sql'
```

Pour le livrable final, remplacer le sample par :

```bash
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
uv run python -m books_catalog_scraper.validate_exports --full
uv run python -m scripts.load_books --input exports/books_details.json
```

## Configuration .env

Le fichier `.env` n'est pas versionne. Il est cree a partir de `.env.example`.

Variables principales :

- `POSTGRES_DB` : nom de la base PostgreSQL locale.
- `POSTGRES_USER` : utilisateur PostgreSQL.
- `POSTGRES_PASSWORD` : mot de passe PostgreSQL.
- `POSTGRES_HOST` : hote utilise par les scripts Python, `localhost` en local.
- `POSTGRES_PORT` : port expose par Docker, `5432` par defaut.

Les reglages Scrapy comme le User-Agent et la temporisation sont places dans
`books_catalog_scraper/settings.py`.

Reglages principaux :

- `ROBOTSTXT_OBEY=True` ;
- `USER_AGENT` explicite pour identifier le projet ;
- `DOWNLOAD_DELAY=0.5` ;
- `RANDOMIZE_DOWNLOAD_DELAY=False` pour garder un rythme rejouable ;
- `CONCURRENT_REQUESTS_PER_DOMAIN=1` pour limiter la charge et garder un ordre
  plus previsible.

## Commandes Scrapy

Lister les spiders disponibles :

```bash
uv run scrapy list
```

Collecter uniquement les pages de liste :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
```

Collecter un echantillon rejouable de 20 fiches produit :

```bash
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
```

Relancer cette commande remplace l'export precedent grace a l'option `-O`.
Le seuil d'erreurs par defaut est `max_errors=50`.

Collecter un echantillon avec un seuil d'erreurs explicite :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
```

Collecter le meme echantillon et le charger dans PostgreSQL :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -s POSTGRES_ENABLED=true -O exports/books_details_sample.json
```

Relancer exactement la meme commande est autorise : l'export est remplace et les
livres deja presents en base sont mis a jour par UPC.

Valider l'echantillon :

```bash
uv run python -m books_catalog_scraper.validate_exports --sample
```

Collecter toutes les fiches produit :

```bash
uv run scrapy crawl books_details -O exports/books_details.json
```

Collecter toutes les fiches avec un seuil d'erreurs explicite :

```bash
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
```

Collecter toutes les fiches et les charger dans PostgreSQL :

```bash
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

Cette commande peut aussi etre relancee apres interruption.

Valider l'export final :

```bash
uv run python -m books_catalog_scraper.validate_exports --full
```

## Exports

Les exports sont separes pour garder des livrables lisibles :

- `exports/books_list.json` : phase 1, 1 000 livres attendus avec titre, prix de
  liste, note et URL produit ;
- `exports/books_details_sample.json` : echantillon de demonstration, meme
  schema que le final, 20 fiches avec la commande documentee ;
- `exports/books_details.json` : resultat final, 1 000 fiches produit attendues.

Le projet utilise toujours `-O` pour produire ces fichiers. Cette option
remplace l'ancien export et rend les commandes rejouables. Eviter `-o` pour ces
livrables afin de ne pas risquer d'ajouter des donnees a un fichier existant.

Les exports JSON sont encodes en UTF-8. Les prix restent des chaines JSON afin
de conserver les valeurs decimales exactes.

Charger un export sample deja produit dans PostgreSQL :

```bash
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
```

Charger l'export final deja produit dans PostgreSQL :

```bash
uv run python -m scripts.load_books --input exports/books_details.json
```

Sequence recommandee avant le chargement PostgreSQL :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
uv run python -m books_catalog_scraper.validate_exports --sample
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
uv run python -m books_catalog_scraper.validate_exports --full
uv run python -m scripts.load_books --input exports/books_details.json
```

Le validateur `--full` echoue clairement si `exports/books_details.json` n'existe
pas encore ou si l'export final est incomplet.

Verifier l'absence de doublons UPC en base :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT COUNT(*) FROM (SELECT upc FROM books GROUP BY upc HAVING COUNT(*) > 1) AS duplicates;"'
```

Lancer les requetes SQL de demonstration :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/demo_queries.sql'
```

Ces requetes ne modifient pas la base. Elles affichent le nombre de livres, les
doublons eventuels, les stocks faibles, les meilleurs livres et des controles
prix/taxe.

## Structure

```text
books_catalog_scraper/   Projet Scrapy
books_catalog_scraper/spiders/
brief/                   Brief ecole
data/raw/                Donnees brutes intermediaires
data/processed/          Donnees nettoyees intermediaires
db/                      Script SQL de creation de la base
docs/                    Documentation du projet
exports/                 Exports JSON
compose.yaml             PostgreSQL local
pyproject.toml           Configuration UV et dependances Python
scrapy.cfg               Point d'entree Scrapy
```

## Documentation

Preparation :

- [01 - Preparation - Installation locale](docs/01-preparation-installation.md)
- [02 - Preparation - Variables d'environnement](docs/02-preparation-environnement.md)
- [03 - Preparation - Fonctionnement prevu](docs/03-preparation-fonctionnement.md)
- [04 - Preparation - Qualite du code](docs/04-preparation-qualite.md)

Phase 1 :

- [05 - Phase 1 - Reconnaissance du site](docs/05-phase-1-reconnaissance.md)
- [06 - Phase 1 - Collecteur des pages de liste](docs/06-phase-1-collecteur-pages-liste.md)

Phase 2 :

- [07 - Phase 2 - Collecteur des fiches produit](docs/07-phase-2-collecteur-fiches-produit.md)
- [08 - Phase 2 - Temporisation et User-Agent](docs/08-phase-2-temporisation-user-agent.md)
- [12 - Phase 2 - Gestion des erreurs](docs/12-phase-2-gestion-erreurs.md)
- [13 - Phase 2 - Stockage PostgreSQL](docs/13-phase-2-stockage-postgresql.md)
- [14 - Phase 2 - Reprise apres interruption](docs/14-phase-2-reprise-apres-interruption.md)
- [15 - Phase 2 - Script de chargement](docs/15-phase-2-script-chargement.md)
- [16 - Phase 2 - Exports](docs/16-phase-2-exports.md)

Livrables :

- [09 - Livrable - Journal de bord](docs/09-livrable-journal-de-bord.md)
- [10 - Livrable - Observations prix et taxe](docs/10-livrable-observations-prix-taxe.md)
- [11 - Correction - Validation des exports](docs/11-correction-validation-exports.md)
- [17 - Livrable - Requetes de demonstration](docs/17-livrable-requetes-demonstration.md)
- [18 - Livrable - Documentation finale](docs/18-livrable-documentation-finale.md)
- [19 - Livrable - Validation finale](docs/19-livrable-validation-finale.md)

## Qualite

Commandes de controle :

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
uv run ruff format .
```

La couverture de tests attendue est configuree a 100%.

## Etat actuel

Etat actuel :

- configuration UV ;
- configuration Docker Compose PostgreSQL ;
- script SQL de creation de la base ;
- collecteur Scrapy des pages de liste ;
- collecteur Scrapy des fiches produit ;
- mode echantillon avec `books_details -a limit=20` ;
- temporisation et User-Agent configures ;
- gestion d'erreurs avec seuil `max_errors` ;
- validateur d'exports JSON ;
- pipeline optionnel de stockage PostgreSQL ;
- reprise apres interruption par upsert PostgreSQL ;
- script de chargement separe ;
- requetes SQL de demonstration ;
- documentation finale ;
- export J1 `exports/books_list.json` ;
- export sample `exports/books_details_sample.json` ;
- export final `exports/books_details.json` ;
- chargement complet des 1 000 livres valide dans PostgreSQL ;
- pytest et coverage configures ;
- documentation de lancement local.

Le full scrape final a ete valide avec 1 000 fiches exportees et 1 000 livres
charges dans PostgreSQL.
