# 14 - Phase 2 - Reprise apres interruption

Partie du brief liee : reprise d'un scraping interrompu et absence de doublons
apres une seconde execution.

## Principe

La reprise repose sur PostgreSQL :

- chaque livre detaille est ecrit en base des son extraction ;
- un `commit` est fait apres chaque item ;
- la cle metier est `books.upc` ;
- l'insertion utilise `ON CONFLICT (upc) DO UPDATE` ;
- le mode `resume_from_db=true` lit les URLs deja presentes dans `books` et ne
  reprogramme pas ces fiches.

Si le scraper est interrompu, les livres deja sauvegardes restent donc en base.

Au lancement suivant, les memes UPC sont mis a jour au lieu d'etre inseres une
seconde fois.

Avec `resume_from_db=true`, le spider evite aussi de revisiter les fiches deja
presentes en base. Il parcourt les pages de liste pour retrouver les liens, mais
il ne lance des requetes produit que pour les fiches manquantes.

## Commandes rejouables

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -s POSTGRES_ENABLED=true -O exports/books_details_sample.json
```

Cette commande peut etre relancee plusieurs fois.

L'export JSON est remplace par `-O`.

Les lignes PostgreSQL existantes sont mises a jour par l'upsert.

Commande de reprise sans revisiter les fiches deja presentes :

```bash
uv run scrapy crawl books_details -a resume_from_db=true -a max_errors=50 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume.json
```

Le fichier de sortie est volontairement place dans `/tmp`, car une reprise peut
ne contenir que les fiches restantes. Cela evite de remplacer
`exports/books_details.json`, qui doit rester l'export final complet.

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

Relancer en mode reprise :

```bash
uv run scrapy crawl books_details -a resume_from_db=true -a limit=3 -a max_errors=5 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume_sample.json
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

- les fiches deja presentes ne sont pas revisitees ;
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

Validation finale de reprise apres full scrape :

```bash
uv run scrapy crawl books_details -a resume_from_db=true -a max_errors=50 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume.json
```

Resultat avec 1 000 livres deja presents en base :

- 50 pages de liste parcourues ;
- 0 fiche produit programmee ;
- 1 000 fiches deja presentes ignorees ;
- 0 echec ;
- 0 livre ajoute, car la base etait deja complete.

## Interruption manuelle

Pour demontrer une interruption sur une collecte plus longue :

```bash
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

Interrompre avec `Ctrl+C`, puis relancer en mode reprise :

```bash
uv run scrapy crawl books_details -a resume_from_db=true -a max_errors=50 -s POSTGRES_ENABLED=true -O /tmp/books_details_resume.json
```

Les livres deja sauvegardes sont ignores cote requetes produit. Les nouveaux
livres sont sauvegardes par upsert.

## Limite assumee

Le crawler reparcourt les pages de liste depuis le debut afin de retrouver les
liens produit. Les fiches produit deja presentes en base ne sont pas revisitees
avec `resume_from_db=true`.

Cette approche reste simple, explicite et suffisante pour le brief.
