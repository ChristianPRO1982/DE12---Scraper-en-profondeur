# 05 - Phase 1 - Reconnaissance du site

Partie du brief liee : phase 1, reconnaissance et cartographie du site avant
ecriture du collecteur de pages de liste.

Site observe : <https://books.toscrape.com/>

Date de reconnaissance : 2026-09-07.

## Politique de crawling

URL testee :

```text
https://books.toscrape.com/robots.txt
```

Resultat observe :

- reponse HTTP `404` ;
- aucun fichier `robots.txt` publie ;
- aucun fichier equivalent n'a ete identifie sur le site ;
- aucune page de politique, conditions d'utilisation ou restriction de crawling
  n'a ete trouvee sur Books to Scrape ;
- aucune directive technique `Disallow` ou `Crawl-delay` n'est donc publiee.

Contexte officiel :

- la page Books to Scrape affiche `We love being scraped!` ;
- elle indique aussi que c'est un site de demonstration pour le web scraping ;
- le site parent <https://toscrape.com/> presente Books to Scrape comme une
  librairie fictive qui veut etre scrapee et comme un environnement sûr pour les
  debutants.

Conclusion :

- il n'y a pas de politique de crawling formalisee sur le site ;
- l'absence de `robots.txt` ne doit pas etre interpretee comme une autorisation
  generale sur n'importe quel site ;
- dans ce cas precis, le contexte officiel confirme que Books to Scrape est un
  bac a sable explicitement destine a l'entrainement au scraping.

Decision pour le projet :

- conserver `ROBOTSTXT_OBEY = True` dans Scrapy ;
- utiliser un User-Agent explicite ;
- conserver une temporisation entre les requetes.

## Catalogue

Point d'entree :

```text
https://books.toscrape.com/
```

Observations :

- la page d'accueil correspond a la page 1 du catalogue ;
- le site annonce `1000 results - showing 1 to 20` ;
- il y a 20 livres par page ;
- la pagination indique `Page 1 of 50` ;
- la page suivante est accessible par un lien `next` ;
- les categories sont listees dans la colonne laterale.

Conclusion :

- il faut suivre le lien `next` avec Scrapy ;
- il ne faut pas construire toutes les URLs a la main ;
- le collecteur de liste doit parcourir 50 pages pour obtenir les 1 000 livres.

## Selecteurs des pages de liste

Chaque livre est dans un bloc :

```text
article.product_pod
```

Champs utiles :

```text
article.product_pod h3 a::attr(title)      titre complet
article.product_pod h3 a::attr(href)       URL relative de la fiche
article.product_pod p.price_color::text    prix de liste
article.product_pod p.star-rating::attr(class) note sous forme de classe CSS
li.next a::attr(href)                      page suivante
```

Point important :

- la note n'est pas un texte ;
- elle est encodee dans une classe CSS comme `star-rating Three` ;
- il faudra convertir `One`, `Two`, `Three`, `Four`, `Five` en `1`, `2`, `3`,
  `4`, `5`.

## URLs produit

Exemple observe sur la page d'accueil :

```text
catalogue/a-light-in-the-attic_1000/index.html
```

Conclusion :

- les URLs produit sont relatives ;
- il faut utiliser `response.urljoin(...)` dans Scrapy ;
- il ne faut pas concatener les chemins manuellement.

## Fiches produit

Exemple observe :

```text
https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
```

Fiches controlees pendant la reconnaissance :

- `A Light in the Attic` ;
- `Tipping the Velvet` ;
- `Soumission`.

Champs visibles sur une fiche :

- titre ;
- prix affiche en haut de fiche ;
- disponibilite detaillee, par exemple `In stock (22 available)` ;
- note CSS ;
- description ;
- categorie dans le fil d'Ariane ;
- table `Product Information`.

Selecteurs utiles :

```text
div.product_main h1::text                         titre
div.product_main p.price_color::text              prix affiche
div.product_main p.instock.availability::text     disponibilite detaillee
div.product_main p.star-rating::attr(class)       note
ul.breadcrumb li a::text                          fil d'Ariane / categorie
div#product_description + p::text                 description
table.table.table-striped tr                      informations produit
```

Dans la table `Product Information`, les libelles a recuperer sont :

```text
UPC
Product Type
Price (excl. tax)
Price (incl. tax)
Tax
Availability
Number of reviews
```

## Champs absents des pages de liste

Les pages de liste affichent seulement une disponibilite simplifiee :

```text
In stock
```

Les fiches produit indiquent le stock reel :

```text
In stock (22 available)
```

Les champs obligatoires qui imposent de visiter les fiches sont donc :

- UPC ;
- stock reel ;
- nombre d'avis ;
- prix hors taxe ;
- prix TTC ;
- taxe ;
- description ;
- categorie.

## Attention sur les prix et la taxe

Sur les premieres fiches observees, les champs `Price (excl. tax)` et
`Price (incl. tax)` peuvent avoir la meme valeur, avec une taxe a `£0.00`.

La note finale demandee par le brief devra verifier ce comportement sur environ
dix livres avant de conclure.
