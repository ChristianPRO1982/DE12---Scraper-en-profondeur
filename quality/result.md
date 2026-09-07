# Résultats de qualité et de validation

Date de contrôle : 2026-09-07.

Ce fichier regroupe les preuves de bon fonctionnement liées aux livrables du
brief : exports, PostgreSQL, reprise, requêtes de démonstration, tests et
couverture.

## 0. Environnement de contrôle

Versions relevées :

```text
uv 0.9.21
Python 3.11.14 via uv run python
Docker Compose version v2.35.1
```

Remarque : la commande `python` seule n'est pas disponible dans cet
environnement. Le projet utilise donc bien `uv run python`, comme documenté dans
le README.

Commande du full scrape validé :

```bash
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

Cette commande a produit l'export final et chargé les données dans PostgreSQL.
Elle reste rejouable grâce à `-O` pour l'export et à l'upsert PostgreSQL.

## 1. Exports JSON

Fichiers présents dans `exports/` :

```text
.gitkeep 1 bytes
books_details.json 1965933 bytes
books_details_sample.json 40423 bytes
books_list.json 198240 bytes
```

Rôles des fichiers :

- `books_list.json` : export de phase 1, 1 000 livres.
- `books_details_sample.json` : export sample, 20 fiches.
- `books_details.json` : export final, 1 000 fiches.

### Validation sample

Commande :

```bash
uv run python -m books_catalog_scraper.validate_exports --sample
```

Résultat :

```text
livres Phase 1 : 1000
URLs Phase 1 uniques : 1000
fiches detaillees : 20
UPC uniques : 20
URLs detaillees uniques : 20
ratings invalides : 0
stocks invalides : 0
reviews invalides : 0
categories absentes : 0
descriptions absentes : 0
prix liste = HT : 20
prix HT = TTC : 20
taxe = 0 : 20
differences prix observees : 0
erreurs : 0
```

### Validation full

Commande :

```bash
uv run python -m books_catalog_scraper.validate_exports --full
```

Résultat :

```text
livres Phase 1 : 1000
URLs Phase 1 uniques : 1000
fiches detaillees : 1000
UPC uniques : 1000
URLs detaillees uniques : 1000
URLs manquantes : 0
URLs supplementaires : 0
ratings invalides : 0
stocks invalides : 0
reviews invalides : 0
categories absentes : 0
descriptions absentes : 2
prix liste = HT : 1000
prix HT = TTC : 1000
taxe = 0 : 1000
differences prix observees : 0
erreurs : 0
```

Conclusion : les exports attendus par le brief sont présents et validés. Les 2
descriptions absentes sont acceptées par le contrat de données, car
`description` peut valoir `null`.

## 2. PostgreSQL

### Tables contrôlées

Le brief demande les 1 000 livres en base PostgreSQL avec UPC, stock réel, note
numérique, nombre d'avis et catégorie.

Commandes de contrôle :

```sql
SELECT COUNT(*) FROM books;
SELECT COUNT(DISTINCT upc) FROM books;
SELECT COUNT(*) FROM categories;
```

Résultats :

```text
books total          : 1000
UPC distincts        : 1000
catégories           : 50
```

### Absence de doublons

Commandes :

```sql
SELECT COUNT(*)
FROM (
    SELECT upc
    FROM books
    GROUP BY upc
    HAVING COUNT(*) > 1
) AS duplicates;
```

```sql
SELECT COUNT(*)
FROM (
    SELECT product_url
    FROM books
    GROUP BY product_url
    HAVING COUNT(*) > 1
) AS duplicates;
```

Résultats :

```text
doublons UPC         : 0
doublons URL produit : 0
```

### Catégories

Extrait de contrôle :

```sql
SELECT id, name
FROM categories
ORDER BY name
LIMIT 10;
```

Résultat :

```text
id,name
533,Academic
86,Add a comment
737,Adult Fiction
76,Art
384,Autobiography
356,Biography
23,Business
72,Childrens
158,Christian
183,Christian Fiction
```

Il y a bien 50 catégories en base. Les valeurs sont conservées telles que
publiées par Books to Scrape, y compris `Default` et `Add a comment`.

### Exemple de livre

Extrait de contrôle :

```sql
SELECT upc, title, category_id, rating, stock_quantity, review_count
FROM books
ORDER BY title
LIMIT 1;
```

Résultat :

```text
upc,title,category_id,rating,stock_quantity,review_count
f16c2edb2a603f92,"Most Blessed of the Patriarchs": Thomas Jefferson and the Empire of the Imagination,25,5,8,0
```

Les champs demandés par le brief sont présents : UPC, titre, catégorie, note,
stock réel et nombre d'avis.

## 3. Requêtes de démonstration

Commande :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/demo_queries.sql'
```

Synthèse des résultats :

```text
Nombre total de livres chargés : 1000
Doublons UPC                   : 0 ligne
Doublons URL produit           : 0 ligne
Livres en stock faible         : 420
Livres notes 4 ou 5            : 375
Catégories                     : 50
```

Contrôle prix et taxe :

```text
price_list = price_excl_tax      : 1000
price_excl_tax = price_incl_tax  : 1000
tax = 0                          : 1000
différences prix/taxe observées  : 0
```

Conclusion : les requêtes permettent de répondre à la question centrale du
brief, notamment les titres en stock faible et les titres les mieux notes.

## 4. Reprise après interruption

Commande de démonstration :

```bash
uv run scrapy crawl books_details -a resume_from_db=true -a max_errors=50 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume.json
```

Résultat observé avec une base déjà complète :

```text
Reprise PostgreSQL active: 1000 fiches déjà présentes
Collecte des listes terminee: 50 pages parcourues, 0 fiches programmees, 1000 deja presentes ignorees, 0 cartes ignorees, 0 doublons URL ignores
0 livres sauvegardes dans PostgreSQL
Collecte des fiches terminee: 0 livres exportes, 0 echecs, raison=finished
```

Conclusion : le mode reprise ne revisite pas les fiches produit déjà présentes
en base. Il parcourt seulement les pages de liste pour retrouver les URLs
produit, puis programme les fiches manquantes.

## 5. Qualité Python

Commandes habituelles :

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
```

Résultat Pytest :

```text
collected 89 items
89 passed in 0.78s
```

Résultat Coverage :

```text
Name                                             Stmts   Miss Branch BrPart  Cover  Missing
--------------------------------------------------------------------------------------------
books_catalog_scraper/__init__.py                    0      0      0      0   100%
books_catalog_scraper/error_policy.py               10      0      4      0   100%
books_catalog_scraper/extractors.py                 13      0      4      0   100%
books_catalog_scraper/parsers.py                    33      0     12      0   100%
books_catalog_scraper/pipelines.py                  32      0      6      0   100%
books_catalog_scraper/postgres.py                   54      0     10      0   100%
books_catalog_scraper/settings.py                   13      0      0      0   100%
books_catalog_scraper/spiders/__init__.py            0      0      0      0   100%
books_catalog_scraper/spiders/books_details.py     130      0     36      0   100%
books_catalog_scraper/spiders/books_list.py         48      0      8      0   100%
books_catalog_scraper/validate_exports.py          225      0     72      0   100%
scripts/__init__.py                                  0      0      0      0   100%
scripts/load_books.py                               32      0      6      0   100%
--------------------------------------------------------------------------------------------
TOTAL                                              590      0    158      0   100%
```

Ruff :

```text
All checks passed!
45 files already formatted
```

Conclusion : lint OK, format OK, tests OK, couverture 100%.

## 6. Git

Derniers commits :

```text
96cd6d2 feat: align project with brief deliverables
f9e2ef1 feat: add code principles documentation and update related files
2d90a3c feat: add final validation documentation and update related files
771c256 feat: update documentation with final deliverables and replayable commands
e31eb03 feat: add demonstration SQL queries and update documentation
```

Conclusion : le projet dispose d'un historique de commits exploitable pour le
brief.

Statut Git au moment de la rédaction de ce rapport :

```text
HEAD : 96cd6d2
git status --short : ?? quality/
```

Le dossier `quality/` est nouveau et doit être ajouté au prochain commit.

## 7. Correspondance avec les critères du brief

| Critère du brief | Preuve |
| --- | --- |
| 1 000 livres collectés | `validate_exports --full` : `fiches detaillees : 1000` |
| 1 000 livres en PostgreSQL | `SELECT COUNT(*) FROM books;` : `1000` |
| UPC récupéré | `COUNT(DISTINCT upc)` : `1000` |
| Stock réel récupéré | champ `stock_quantity`, vue `books_stock_alerts` |
| Note numérique | validateur : `ratings invalides : 0` |
| Nombre d'avis | champ `review_count`, validateur : `reviews invalides : 0` |
| Catégories | `SELECT COUNT(*) FROM categories;` : `50` |
| Pas de doublons | doublons UPC : `0`, doublons URL : `0` |
| Mode échantillon | sample validé : `fiches détaillées : 20` |
| Reprise après interruption | `resume_from_db=true` : `0 fiches programmees`, `1000 deja presentes ignorees` |
| User-Agent explicite | documenté dans `docs/08-phase-2-temporisation-user-agent.md` |
| Temporisation justifiée | documentée dans `docs/08-phase-2-temporisation-user-agent.md` |
| Script de création BDD | `db/schema.sql` |
| Script de chargement | `scripts/load_books.py` |
| Requêtes de démonstration | `db/demo_queries.sql` |
| Journal de bord | `docs/09-livrable-journal-de-bord.md` |
| Note prix/taxe | `docs/10-livrable-observations-prix-taxe.md` |
| Qualité | Ruff OK, `89 passed`, Coverage `100%` |

## 8. Conclusion générale

Les livrables du brief sont couverts :

- repo UV/Scrapy/PostgreSQL/Docker ;
- README avec installation, lancement local et auteur ;
- collecteur de pages de liste ;
- collecteur de fiches produit ;
- mode sample ;
- exports JSON dans le repo ;
- script SQL de création de base ;
- script de chargement PostgreSQL ;
- 1 000 livres chargés en base ;
- reprise après interruption démontrable ;
- User-Agent et temporisation justifiés ;
- journal de bord ;
- note prix/taxe ;
- requêtes SQL de démonstration ;
- tests, Ruff et Coverage OK.
