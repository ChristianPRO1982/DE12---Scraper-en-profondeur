# 07 - Livrable - Journal de bord

Partie du brief liee : livrable final et suivi des blocages, essais et
decisions pendant J1 et J2.

## J1

### Reconnaissance

Reconnaissance realisee le 2026-09-07.

- Politique de crawling : l'URL `https://books.toscrape.com/robots.txt` repond
  en 404. Aucun fichier equivalent, aucune page de conditions d'utilisation et
  aucune restriction de crawling n'ont ete identifies sur Books to Scrape.
- Contexte officiel : Books to Scrape affiche `We love being scraped!` et le
  site parent `toscrape.com` le presente comme une librairie fictive destinee au
  scraping et sure pour les debutants.
- Pagination : le catalogue annonce 1 000 resultats, 20 livres par page et 50
  pages.
- Navigation : la page suivante est disponible via le lien `next`.
- Liens produit : les liens vers les fiches sont relatifs, par exemple
  `catalogue/a-light-in-the-attic_1000/index.html`.
- Pages de liste : elles contiennent titre, prix de liste, note CSS,
  disponibilite simplifiee et URL de fiche.
- Fiches produit : `A Light in the Attic`, `Tipping the Velvet` et `Soumission`
  ont ete controlees. Elles contiennent les champs manquants du brief, notamment
  UPC, stock reel, nombre d'avis, prix HT, prix TTC, taxe, description et
  categorie.

Details notes dans `05-phase-1-reconnaissance.md`.

### Collecte des pages de liste

Collecteur realise le 2026-09-07.

- Spider cree : `books_list`.
- Commande de lancement :
  `uv run scrapy crawl books_list -O exports/books_list.json`.
- Pagination : le spider suit le lien `li.next a` avec `response.follow`.
- URLs produit : les liens relatifs sont transformes avec `response.urljoin`.
- Note : la classe CSS `star-rating One/Two/Three/Four/Five` est convertie en
  nombre entier.
- Prix : le prix de liste est converti avec `Decimal`, puis exporte en texte
  dans le JSON pour conserver une valeur exacte.
- Robustesse : une carte produit mal formee est journalisee et ignoree, sans
  faire tomber toute la page.
- Export obtenu : `exports/books_list.json`.
- Resultat verifie : 1 000 livres collectes, 50 pages parcourues, 0 livre
  ignore, 0 URL dupliquee.

Details notes dans `06-phase-1-collecteur-pages-liste.md`.

## J2

### Collecte des fiches produit

A completer pendant l'implementation.

### Reprise apres interruption

A completer pendant l'implementation et la demonstration.

### Chargement PostgreSQL

A completer pendant l'implementation.

## Blocages rencontres

A completer au fil du projet.
