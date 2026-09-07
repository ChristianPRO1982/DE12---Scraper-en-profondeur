# Scraper en profondeur - Books to Scrape

Projet d'ecole pour apprendre a scraper un catalogue en profondeur avec
Scrapy, PostgreSQL, Docker et UV.

Le site cible est le bac a sable legal d'entrainement :
<https://books.toscrape.com/>

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

A ce stade, aucun spider de production n'est encore implemente. La commande peut
donc ne lister aucun spider, ce qui est normal pour cette premiere structure.

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

## Structure

```text
books_catalog_scraper/   Projet Scrapy
books_catalog_scraper/spiders/
brief/                   Brief ecole
data/raw/                Donnees brutes intermediaires
data/processed/          Donnees nettoyees intermediaires
db/                      Script SQL de creation de la base
docs/                    Documentation du projet
exports/                 Futurs exports CSV ou JSON
compose.yaml             PostgreSQL local
pyproject.toml           Configuration UV et dependances Python
scrapy.cfg               Point d'entree Scrapy
```

## Documentation

- [docs/installation.md](docs/installation.md)
- [docs/fonctionnement.md](docs/fonctionnement.md)
- [docs/environnement.md](docs/environnement.md)
- [docs/qualite.md](docs/qualite.md)
- [docs/journal-de-bord.md](docs/journal-de-bord.md)
- [docs/observations-prix-taxe.md](docs/observations-prix-taxe.md)

## Qualite

Commandes de controle :

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
uv run ruff format .
```

La couverture de tests attendue est configuree a 100%.

## Etat actuel

Structure initiale uniquement :

- configuration UV ;
- configuration Docker Compose PostgreSQL ;
- script SQL de creation de la base ;
- projet Scrapy vide ;
- pytest et coverage configures ;
- documentation de lancement local.

Le scraping, les pipelines et le chargement en base ne sont pas
encore developpes.
