# 17 - Livrable - Requetes de demonstration

Partie du brief liee : verification du chargement PostgreSQL et exploitation
des donnees collectees.

## Objectif

Les requetes de demonstration doivent permettre de verifier rapidement que les
donnees chargees en base sont coherentes et exploitables.

Elles sont regroupees dans un fichier rejouable :

```text
db/demo_queries.sql
```

## Commande

Lancer toutes les requetes :

```bash
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/demo_queries.sql'
```

Cette commande ne modifie aucune donnee. Elle peut etre relancee apres un sample,
apres une interruption ou apres le full scrape final.

## Requetes incluses

Le fichier SQL affiche :

- le nombre total de livres charges ;
- les doublons UPC eventuels ;
- les doublons d'URL produit eventuels ;
- les livres en rupture ou en stock faible ;
- les livres les mieux notes ;
- la repartition des livres par categorie ;
- un controle des prix et de la taxe.

## Lecture attendue

Apres un chargement sample, le nombre total de livres depend de la limite
utilisee.

Apres le chargement final attendu par le brief :

- `total_books` doit valoir `1000` ;
- la requete des doublons UPC ne doit retourner aucune ligne ;
- la requete des doublons URL produit ne doit retourner aucune ligne ;
- les vues `books_stock_alerts` et `books_best_rated` doivent retourner des
  livres exploitables pour la demonstration.

## Requetes principales

Livres en stock faible :

```sql
SELECT *
FROM books_stock_alerts
ORDER BY stock_quantity ASC, rating DESC;
```

Livres les mieux notes :

```sql
SELECT *
FROM books_best_rated
ORDER BY rating DESC, review_count DESC, title ASC;
```

Nombre total de livres :

```sql
SELECT COUNT(*) AS total_books
FROM books;
```

Doublons UPC :

```sql
SELECT upc, COUNT(*)
FROM books
GROUP BY upc
HAVING COUNT(*) > 1;
```
