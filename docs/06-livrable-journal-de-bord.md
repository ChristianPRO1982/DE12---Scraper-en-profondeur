# 06 - Livrable - Journal de bord

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
  scraping et sûre pour les debutants.
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

Details notes dans `docs/05-phase-1-reconnaissance.md`.

### Collecte des pages de liste

A completer pendant l'implementation.

## J2

### Collecte des fiches produit

A completer pendant l'implementation.

### Reprise apres interruption

A completer pendant l'implementation et la demonstration.

### Chargement PostgreSQL

A completer pendant l'implementation.

## Blocages rencontres

A completer au fil du projet.
