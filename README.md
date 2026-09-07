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

Valider l'echantillon :

```bash
uv run python -m books_catalog_scraper.validate_exports --sample
```

Collecter toutes les fiches produit :

```bash
uv run scrapy crawl books_details -O exports/books_details.json
```

Valider l'export final :

```bash
uv run python -m books_catalog_scraper.validate_exports --full
```

Sequence recommandee avant le chargement PostgreSQL :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
uv run python -m books_catalog_scraper.validate_exports --sample
uv run scrapy crawl books_details -O exports/books_details.json
uv run python -m books_catalog_scraper.validate_exports --full
```

Le validateur `--full` echoue clairement si `exports/books_details.json` n'existe
pas encore ou si l'export final est incomplet.

## Structure

```text
books_catalog_scraper/   Projet Scrapy
books_catalog_scraper/spiders/
brief/                   Brief ecole
data/raw/                Donnees brutes intermediaires
data/processed/          Donnees nettoyees intermediaires
db/                      Script SQL de creation de la base
docs/                    Documentation du projet
exports/                 Exports CSV ou JSON
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

Livrables :

- [09 - Livrable - Journal de bord](docs/09-livrable-journal-de-bord.md)
- [10 - Livrable - Observations prix et taxe](docs/10-livrable-observations-prix-taxe.md)
- [11 - Correction - Validation des exports](docs/11-correction-validation-exports.md)

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
- validateur d'exports JSON ;
- export J1 `exports/books_list.json` ;
- pytest et coverage configures ;
- documentation de lancement local.

Le pipeline PostgreSQL et le chargement en base ne sont pas encore developpes.
