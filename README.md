# Scraper en profondeur - Books to Scrape

Projet d'école pour apprendre à scraper un catalogue en profondeur avec
Scrapy, PostgreSQL, Docker et UV.

Le site cible est le bac à sable légal d'entraînement :
<https://books.toscrape.com/>

Dépôt du projet :
<https://github.com/ChristianPRO1982/DE12---Scraper-en-profondeur>

Auteur : ChristianPRO1982.

## Objectif

Le projet doit collecter les livres du catalogue, visiter les fiches produit,
récupérer les informations absentes des pages de liste, puis charger le résultat
dans PostgreSQL.

Le développement suivra le brief fourni dans [brief/brief.md](brief/brief.md).

## Technologies

- Python géré avec UV
- Scrapy pour le scraping
- PostgreSQL pour le stockage
- Docker Compose pour lancer la base en local
- Pas de Node.js

## Installation locale

Prérequis attendus :

- Python 3.11 ou plus récent
- UV
- Docker avec Docker Compose

Configurer l'environnement :

```bash
cp .env.example .env
```

Installer les dépendances Python :

```bash
uv sync
```

Lancer PostgreSQL :

```bash
docker compose up -d
```

Créer les tables :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
```

Vérifier que le projet Scrapy est visible :

```bash
uv run scrapy list
```

La commande doit lister les spiders `books_list` et `books_details`.

## Parcours complet rejouable

Séquence courte depuis un projet configuré :

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

Pour démontrer la reprise après interruption sans revisiter les fiches déjà
présentes en base :

```bash
uv run scrapy crawl books_details -a resume_from_db=true -a max_errors=50 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume.json
```

Cette commande lit les `product_url` déjà stockées dans PostgreSQL, saute les
fiches déjà collectées et ne programme que les fiches manquantes. Utiliser un
fichier temporaire évite de remplacer l'export final complet par un export de
reprise partiel.

## Configuration .env

Le fichier `.env` n'est pas versionné. Il est créé à partir de `.env.example`.

Variables principales :

- `POSTGRES_DB` : nom de la base PostgreSQL locale.
- `POSTGRES_USER` : utilisateur PostgreSQL.
- `POSTGRES_PASSWORD` : mot de passe PostgreSQL.
- `POSTGRES_HOST` : hôte utilisé par les scripts Python, `localhost` en local.
- `POSTGRES_PORT` : port exposé par Docker, `5432` par défaut.

Les réglages Scrapy comme le User-Agent et la temporisation sont placés dans
`books_catalog_scraper/settings.py`.

Réglages principaux :

- `ROBOTSTXT_OBEY=True` ;
- `USER_AGENT` explicite pour identifier le projet ;
- `DOWNLOAD_DELAY=0.5` ;
- `RANDOMIZE_DOWNLOAD_DELAY=False` pour garder un rythme rejouable ;
- `CONCURRENT_REQUESTS_PER_DOMAIN=1` pour limiter la charge et garder un ordre
  plus prévisible.

## Commandes Scrapy

Lister les spiders disponibles :

```bash
uv run scrapy list
```

Collecter uniquement les pages de liste :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
```

Collecter un échantillon rejouable de 20 fiches produit :

```bash
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
```

Relancer cette commande remplace l'export précédent grâce à l'option `-O`.
Le seuil d'erreurs par défaut est `max_errors=50`.

Collecter un échantillon avec un seuil d'erreurs explicite :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
```

Collecter le même échantillon et le charger dans PostgreSQL :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -s POSTGRES_ENABLED=true -O exports/books_details_sample.json
```

Relancer exactement la même commande est autorisé : l'export est remplacé et les
livres déjà présents en base sont mis à jour par UPC.

Valider l'échantillon :

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

Cette commande peut aussi être relancée après interruption.

Reprendre une collecte PostgreSQL sans revisiter les fiches déjà présentes :

```bash
uv run scrapy crawl books_details -a resume_from_db=true -a max_errors=50 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume.json
```

Cette commande sert à la démonstration de reprise. Elle écrit seulement les
fiches restantes dans l'export temporaire.

Valider l'export final :

```bash
uv run python -m books_catalog_scraper.validate_exports --full
```

## Exports

Les exports sont séparés pour garder des livrables lisibles :

- `exports/books_list.json` : phase 1, 1 000 livres attendus avec titre, prix de
  liste, note et URL produit ;
- `exports/books_details_sample.json` : échantillon de démonstration, même
  schéma que le final, 20 fiches avec la commande documentée ;
- `exports/books_details.json` : résultat final, 1 000 fiches produit attendues.

Le projet utilise toujours `-O` pour produire ces fichiers. Cette option
remplace l'ancien export et rend les commandes rejouables. Éviter `-o` pour ces
livrables afin de ne pas risquer d'ajouter des données à un fichier existant.

Les exports JSON sont encodés en UTF-8. Les prix restent des chaînes JSON afin
de conserver les valeurs décimales exactes.

Charger un export sample déjà produit dans PostgreSQL :

```bash
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
```

Charger l'export final déjà produit dans PostgreSQL :

```bash
uv run python -m scripts.load_books --input exports/books_details.json
```

Séquence recommandée avant le chargement PostgreSQL :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
uv run python -m books_catalog_scraper.validate_exports --sample
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
uv run python -m books_catalog_scraper.validate_exports --full
uv run python -m scripts.load_books --input exports/books_details.json
```

Le validateur `--full` échoue clairement si `exports/books_details.json` n'existe
pas encore ou si l'export final est incomplet.

Vérifier l'absence de doublons UPC en base :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -tAc "SELECT COUNT(*) FROM (SELECT upc FROM books GROUP BY upc HAVING COUNT(*) > 1) AS duplicates;"'
```

Lancer les requêtes SQL de démonstration :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/demo_queries.sql'
```

Ces requêtes ne modifient pas la base. Elles affichent le nombre de livres, les
doublons éventuels, les stocks faibles, les meilleurs livres et des contrôles
prix/taxe.

## Structure

```text
books_catalog_scraper/   Projet Scrapy
books_catalog_scraper/spiders/
brief/                   Brief école
data/raw/                Données brutes intermédiaires
data/processed/          Données nettoyées intermédiaires
db/                      Script SQL de création de la base
docs/                    Documentation du projet
exports/                 Exports JSON
quality/                 Résultats de qualité et validation finale
compose.yaml             PostgreSQL local
pyproject.toml           Configuration UV et dépendances Python
scrapy.cfg               Point d'entrée Scrapy
```

## Documentation

Préparation :

- [01 - Préparation - Installation locale](docs/01-preparation-installation.md)
- [02 - Préparation - Variables d'environnement](docs/02-preparation-environnement.md)
- [03 - Préparation - Fonctionnement prévu](docs/03-preparation-fonctionnement.md)
- [04 - Préparation - Qualité du code](docs/04-preparation-qualite.md)

Phase 1 :

- [05 - Phase 1 - Reconnaissance du site](docs/05-phase-1-reconnaissance.md)
- [06 - Phase 1 - Collecteur des pages de liste](docs/06-phase-1-collecteur-pages-liste.md)

Phase 2 :

- [07 - Phase 2 - Collecteur des fiches produit](docs/07-phase-2-collecteur-fiches-produit.md)
- [08 - Phase 2 - Temporisation et User-Agent](docs/08-phase-2-temporisation-user-agent.md)
- [12 - Phase 2 - Gestion des erreurs](docs/12-phase-2-gestion-erreurs.md)
- [13 - Phase 2 - Stockage PostgreSQL](docs/13-phase-2-stockage-postgresql.md)
- [14 - Phase 2 - Reprise après interruption](docs/14-phase-2-reprise-apres-interruption.md)
- [15 - Phase 2 - Script de chargement](docs/15-phase-2-script-chargement.md)
- [16 - Phase 2 - Exports](docs/16-phase-2-exports.md)

Livrables :

- [09 - Livrable - Journal de bord](docs/09-livrable-journal-de-bord.md)
- [10 - Livrable - Observations prix et taxe](docs/10-livrable-observations-prix-taxe.md)
- [11 - Correction - Validation des exports](docs/11-correction-validation-exports.md)
- [17 - Livrable - Requêtes de démonstration](docs/17-livrable-requetes-demonstration.md)
- [18 - Livrable - Documentation finale](docs/18-livrable-documentation-finale.md)
- [19 - Livrable - Validation finale](docs/19-livrable-validation-finale.md)
- [20 - Livrable - Principes de code](docs/20-livrable-principes-code.md)
- [Résultats qualité et validation](quality/result.md)

## Qualité

Commandes de contrôle :

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
uv run ruff format .
```

La couverture de tests attendue est configurée à 100%.

Les résultats détaillés de validation sont consignés dans
[quality/result.md](quality/result.md).

## État actuel

État actuel :

- configuration UV ;
- configuration Docker Compose PostgreSQL ;
- script SQL de création de la base ;
- collecteur Scrapy des pages de liste ;
- collecteur Scrapy des fiches produit ;
- mode échantillon avec `books_details -a limit=20` ;
- temporisation et User-Agent configurés ;
- gestion d'erreurs avec seuil `max_errors` ;
- validateur d'exports JSON ;
- pipeline optionnel de stockage PostgreSQL ;
- reprise après interruption par upsert PostgreSQL ;
- script de chargement séparé ;
- requêtes SQL de démonstration ;
- documentation finale ;
- principes de code documentés ;
- export J1 `exports/books_list.json` ;
- export sample `exports/books_details_sample.json` ;
- export final `exports/books_details.json` ;
- chargement complet des 1 000 livres validé dans PostgreSQL ;
- pytest et coverage configurés ;
- documentation de lancement local.

Le full scrape final a été validé avec 1 000 fiches exportées et 1 000 livres
chargés dans PostgreSQL.
