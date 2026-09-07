# 01 - Preparation - Installation locale

Partie du brief liee : preparation du socle technique, installation depuis zero.

Ce projet doit rester simple a lancer sur une machine de developpement standard.
Il n'utilise pas Node.js et ne demande pas de mise a niveau systeme particuliere.

## Prerequis

- Python 3.11 ou plus recent
- UV
- Docker avec Docker Compose

## Etapes

Depuis la racine du projet :

```bash
cp .env.example .env
uv sync
docker compose up -d
```

Verifier que PostgreSQL tourne :

```bash
docker compose ps
```

Creer le schema de base de donnees :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
```

Verifier que Scrapy charge le projet :

```bash
uv run scrapy list
```

Au stade de la structure initiale, aucun spider n'est encore cree. Une liste vide
est donc normale.

## Arret de PostgreSQL

```bash
docker compose down
```

Pour supprimer aussi les donnees PostgreSQL locales :

```bash
docker compose down -v
```
