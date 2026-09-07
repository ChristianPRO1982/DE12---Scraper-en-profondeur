# 20 - Livrable - Principes de code

Partie du brief liee : lisibilite, robustesse, qualite du code et projet simple
a reprendre par un debutant en Scrapy.

## Objectif

Le code doit rester robuste sans devenir difficile a lire. Le projet evite les
abstractions avancees et garde des fichiers courts, nommes selon leur role.

## Organisation retenue

Le code applicatif est limite a quelques modules :

- `books_catalog_scraper/spiders/books_list.py` : collecte les pages de liste ;
- `books_catalog_scraper/spiders/books_details.py` : collecte les fiches produit ;
- `books_catalog_scraper/extractors.py` : extraction d'une carte de liste ;
- `books_catalog_scraper/parsers.py` : conversions simples et testables ;
- `books_catalog_scraper/error_policy.py` : seuil d'erreurs ;
- `books_catalog_scraper/postgres.py` : configuration et SQL PostgreSQL ;
- `books_catalog_scraper/pipelines.py` : pipeline Scrapy optionnel ;
- `books_catalog_scraper/validate_exports.py` : validation des exports ;
- `scripts/load_books.py` : chargement PostgreSQL depuis un export.

Cette organisation permet de lire le projet dans l'ordre du brief : liste,
details, exports, base, validation.

## Choix de simplicite

- Pas d'ORM : les requetes SQL restent visibles.
- Pas de framework de migration : le schema est dans `db/schema.sql`.
- Pas de table intermediaire : les livres valides sont charges directement.
- Pas de dependance exotique : Scrapy, psycopg, Pytest, Coverage et Ruff.
- Pas de Node.js.
- Pas de conversion en `float` pour les prix : `Decimal` cote Python, chaines
  JSON dans les exports.
- Pas de nettoyage metier destructeur : les descriptions et categories publiees
  par le site sont conservees.

## Robustesse

Les erreurs previsibles sont traitees pres de leur source :

- champ obligatoire absent ;
- prix invalide ;
- note introuvable ;
- stock introuvable ;
- fiche produit mal formee ;
- export JSON incomplet ;
- variable d'environnement PostgreSQL manquante.

Les spiders acceptent `max_errors`. Une anomalie isolee est journalisee et
ignoree, mais le spider s'arrete si le seuil est depasse.

## Rejouabilite

Le code garde les executions rejouables :

- les exports Scrapy utilisent `-O` pour remplacer le fichier cible ;
- `db/schema.sql` est idempotent ;
- PostgreSQL utilise `ON CONFLICT (upc) DO UPDATE` ;
- le script `scripts.load_books` reutilise les memes upserts que le pipeline ;
- les validations peuvent etre relancees sans modifier les donnees.

## Tests

Les fonctions de parsing et les comportements importants sont couverts par des
tests unitaires :

- conversion des prix ;
- conversion des notes ;
- extraction du stock ;
- extraction des fiches ;
- seuil d'erreurs ;
- validation des exports ;
- chargement PostgreSQL ;
- pipeline Scrapy.

La couverture attendue est `100%`.

## Commandes de verification

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
```

## Limites assumees

La reprise apres interruption reparcourt les pages depuis le debut. Ce choix est
volontaire pour garder le code simple. L'absence de doublons reste garantie par
l'upsert PostgreSQL sur `books.upc`.

Le validateur est volontairement separe du scraping. Il rend les exports
controlables sans relancer de crawl.
