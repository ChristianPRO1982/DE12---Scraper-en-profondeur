# 07 - Phase 2 - Collecteur des fiches produit

Partie du brief liee : phase 2, scraping en profondeur des fiches produit.

## Objectif

Le spider `books_details` enrichit les donnees des pages de liste avec les
informations disponibles uniquement sur les fiches produit.

Il part du catalogue, suit la pagination par le lien `next`, puis visite chaque
fiche produit trouvee sur les pages de liste.

## Commande

```bash
uv run scrapy crawl books_details -O exports/books_details.json
```

## Mode echantillon

Pour tester rapidement le spider sans collecter les 1 000 fiches, utiliser le
parametre `limit`.

```bash
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
```

Le parametre `limit` controle le nombre de fiches produit programmees par le
spider.

L'option `-O` ecrase l'export precedent. La commande est donc rejouable sans
nettoyage manuel.

## Champs extraits

Pour chaque livre, le spider produit :

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

## Points d'attention couverts

- Le spider suit le lien `next`, il ne fabrique pas les URLs de pagination a la
  main.
- Les URLs relatives sont resolues avec les outils Scrapy (`response.follow` et
  `response.urljoin`).
- Le titre des pages de liste vient de l'attribut `title`, pas du texte tronque
  affiche dans la carte.
- La note vient de la classe CSS `star-rating One/Two/Three/Four/Five`, puis
  elle est convertie en entier.
- Le stock reel vient de la fiche produit, pas de la mention simplifiee de la
  page de liste.
- L'UPC est extrait et servira de cle fonctionnelle pour la base.
- La table `Product Information` est lue par libelle `th`, pas par position de
  ligne.
- Les prix sont convertis avec `Decimal`, pas avec `float`.
- Le nombre d'avis est converti en entier.
- La description est optionnelle : si elle est absente, la valeur exportee est
  `None`.
- La categorie vient du fil d'Ariane, en excluant `Home` et `Books`.
- Les espaces sont nettoyes sans transformer fortement le texte.
- Une carte ou une fiche mal formee est journalisee puis ignoree.

## Validation realisee

Tests locaux :

```bash
uv run ruff check .
uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
```

Validation reseau courte avec le mode `limit` :

```bash
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
```

Validation realisee le 2026-09-07 :

- 1 page de liste parcourue ;
- 20 fiches programmees ;
- 20 livres exportes ;
- 0 echec d'extraction.

La commande peut etre relancee a tout moment.

## Limites restantes

Cette etape ne charge pas encore les donnees dans PostgreSQL.

La reprise apres interruption sera traitee avec le pipeline PostgreSQL et
l'upsert sur `books.upc`.
