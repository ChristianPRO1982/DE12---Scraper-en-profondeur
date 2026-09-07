# 06 - Phase 1 - Collecteur des pages de liste

Partie du brief liee : phase 1, collecte des 50 pages de liste et production
d'un fichier contenant les 1 000 livres avec leur URL de fiche.

## Commande

```bash
uv run scrapy crawl books_list -O exports/books_list.json
```

## Spider

Spider implemente :

```text
books_catalog_scraper/spiders/books_list.py
```

Nom Scrapy :

```text
books_list
```

## Donnees extraites

Pour chaque livre des pages de liste, le spider extrait :

- `title` : titre complet depuis l'attribut `title` du lien ;
- `price_list` : prix affiche sur la liste, converti en `Decimal` dans le code
  puis exporte en texte dans le JSON pour conserver une valeur exacte ;
- `rating` : note numerique de 1 a 5 ;
- `product_url` : URL absolue de la fiche produit.

Exemple :

```json
{
  "title": "A Light in the Attic",
  "price_list": "51.77",
  "rating": 3,
  "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
}
```

## Difficultes du brief prises en compte

### Note encodee dans une classe CSS

La note n'est pas lue dans le texte visible. Elle est extraite depuis la classe :

```text
p.star-rating::attr(class)
```

Puis elle est convertie avec une table simple :

```text
One -> 1
Two -> 2
Three -> 3
Four -> 4
Five -> 5
```

### URL produit relative

Les liens de fiche produit sont relatifs, par exemple :

```text
catalogue/a-light-in-the-attic_1000/index.html
```

Le spider utilise `response.urljoin(...)` pour obtenir une URL absolue. Cela
evite les erreurs de concatenation manuelle.

### Pagination via lien next

Le spider ne fabrique pas les 50 URLs a la main. Il suit le lien :

```text
li.next a::attr(href)
```

Cela respecte l'observation faite pendant la reconnaissance.

### Prix traite comme une valeur decimale

Le prix de liste est converti avec `Decimal`, pas avec `float`. Cela evite les
approximations binaires inutiles sur les montants.

### Disponibilite incomplete sur les listes

Les pages de liste affichent seulement `In stock`. Le stock reel n'est pas
collecte dans cette phase, car le brief indique qu'il se trouve sur les fiches
produit. Cette information sera traitee en phase 2.

### Carte produit invalide

Si une carte produit contient un champ obligatoire absent ou une valeur impossible
a convertir, elle est journalisee puis ignoree. Cela evite qu'une anomalie locale
arrete toute la page de catalogue.

## Resultat obtenu

Commande executee avec succes :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
```

Resultat verifie :

- 50 pages de liste parcourues ;
- 20 livres trouves par page ;
- 1 000 livres exportes ;
- 0 URL produit dupliquee ;
- 0 livre ignore ;
- fichier JSON valide : `exports/books_list.json`.

## Tests

Les fonctions de conversion et le spider sont couverts par les tests :

- `tests/test_parsers.py` ;
- `tests/test_books_list_spider.py`.

La couverture reste a 100%.
