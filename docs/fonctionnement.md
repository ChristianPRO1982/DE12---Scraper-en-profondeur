# Fonctionnement prevu

Le projet suivra les deux phases du brief.

## Phase 1

Le collecteur de pages de liste devra parcourir les pages du catalogue Books to
Scrape et produire, pour chaque livre :

- titre ;
- prix affiche sur la liste ;
- note numerique convertie depuis la classe CSS ;
- URL de la fiche produit.

## Phase 2

Le collecteur de fiches produit devra visiter chaque fiche et enrichir les
donnees avec :

- UPC ;
- prix hors taxe ;
- prix TTC ;
- taxe ;
- stock reel ;
- nombre d'avis ;
- description ;
- categorie.

## Reprise apres interruption

La reprise devra etre effective et demonstrable. La cle fonctionnelle retenue
sera l'UPC, car le brief indique que le titre n'est pas une cle fiable.

Le mecanisme exact sera implemente plus tard avec le scraper et le chargement en
base.

## Base de donnees

PostgreSQL est lance par Docker Compose.

Le schema est cree par [../db/schema.sql](../db/schema.sql). Il contient :

- `categories` : les categories du catalogue ;
- `books` : les livres collectes, avec `upc` comme cle primaire ;
- `books_catalog` : vue de lecture avec le nom de categorie ;
- `books_stock_alerts` : vue des livres en rupture ou en stock faible ;
- `books_best_rated` : vue des livres notes 4 ou 5.

Il n'y a pas de table intermediaire. Le chargement devra inserer directement les
categories et les livres, puis utiliser `ON CONFLICT` sur `books.upc` pour rendre
les executions successives idempotentes.
