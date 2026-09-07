# 11 - Correction - Validation des exports

Partie du brief liee : fiabilisation des livrables avant le scraping complet et
le chargement PostgreSQL.

## Exports attendus

Le projet conserve trois exports distincts :

- `exports/books_list.json` : export de la phase 1, attendu avec 1 000 livres ;
- `exports/books_details_sample.json` : export de demonstration limite ;
- `exports/books_details.json` : export final, attendu avec 1 000 fiches.

Le sample ne remplace pas l'export final.

## Commandes rejouables

```bash
uv run scrapy crawl books_list -O exports/books_list.json
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
uv run python -m books_catalog_scraper.validate_exports --sample
uv run scrapy crawl books_details -O exports/books_details.json
uv run python -m books_catalog_scraper.validate_exports --full
```

L'option Scrapy `-O` ecrase le fichier cible. Elle evite d'ajouter une nouvelle
collecte a la suite de l'ancienne.

## Validation sample

```bash
uv run python -m books_catalog_scraper.validate_exports --sample
```

Ce mode valide :

- `exports/books_list.json` avec 1 000 livres ;
- `exports/books_details_sample.json` avec au moins une fiche ;
- le schema detaille ;
- les types et contraintes metier ;
- les titres communs entre liste et fiches.

Il n'exige pas 1 000 fiches detaillees pour le sample.

## Validation full

```bash
uv run python -m books_catalog_scraper.validate_exports --full
```

Ce mode valide :

- `exports/books_list.json` avec 1 000 livres ;
- `exports/books_details.json` avec 1 000 fiches ;
- 1 000 UPC uniques ;
- 1 000 URLs detaillees uniques ;
- les memes URLs entre la phase 1 et la phase 2 ;
- 0 champ obligatoire invalide.

Si `exports/books_details.json` est absent, la commande retourne un code erreur.
Dans ce cas, le resume indique les 1 000 URLs manquantes mais l'affichage detaille
est limite aux premieres erreurs pour rester lisible.

## Contrat des fiches detaillees

Les exports `books_details_sample.json` et `books_details.json` doivent avoir le
meme schema exact :

- `upc` ;
- `title` ;
- `product_url` ;
- `category` ;
- `rating` ;
- `price_list` ;
- `price_excl_tax` ;
- `price_incl_tax` ;
- `tax` ;
- `stock_quantity` ;
- `availability_text` ;
- `review_count` ;
- `description` ;
- `image_url`.

Les prix restent des valeurs exactes : `Decimal` dans le code Python, puis texte
dans le JSON Scrapy.

## Resume affiche

Le validateur affiche un resume lisible :

- nombre de livres phase 1 ;
- nombre d'URLs uniques ;
- nombre de fiches detaillees ;
- nombre d'UPC uniques ;
- URLs manquantes ou supplementaires en mode full ;
- ratings, stocks, reviews et categories invalides ;
- descriptions absentes ;
- statistiques sur les prix et la taxe ;
- nombre total d'erreurs.
