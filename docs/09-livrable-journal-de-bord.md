# 09 - Livrable - Journal de bord

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

Collecteur realise le 2026-09-07.

- Spider cree : `books_details`.
- Commande de lancement complete :
  `uv run scrapy crawl books_details -O exports/books_details.json`.
- Parcours : le spider part des pages de liste, extrait les liens produit, puis
  visite les fiches avec `response.follow`.
- URLs produit : les liens relatifs sont dedupliques apres resolution en URL
  absolue.
- Champs extraits : UPC, titre, URL produit, categorie, note numerique, prix de
  liste, prix HT, prix TTC, taxe, stock reel, nombre d'avis, description et URL
  image.
- Table `Product Information` : les valeurs sont lues par libelle `th`, pas par
  position de ligne.
- Categorie : elle est extraite du fil d'Ariane, en ignorant `Home` et `Books`.
- Stock reel : il est extrait depuis le texte de disponibilite de la fiche, par
  exemple `In stock (22 available)`.
- Robustesse : une carte de liste ou une fiche invalide est journalisee et
  ignoree, sans arreter toute la collecte.
- Validation locale : tests unitaires et tests spider passent.
- Validation reseau : un crawl d'echantillon a exporte 18 fiches reelles avec 0
  echec avant arret automatique Scrapy.

Details notes dans `07-phase-2-collecteur-fiches-produit.md`.

### Mode echantillon

Mode echantillon realise le 2026-09-07.

- Parametre ajoute : `limit`.
- Commande rejouable :
  `uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json`.
- Effet : le spider programme au maximum 20 fiches produit.
- Rejouabilite : l'option Scrapy `-O` remplace l'export precedent a chaque
  lancement.
- Validation locale : tests ajoutes sur la limite et le rejet d'une limite non
  positive.
- Validation reseau : `limit=20` a exporte 20 livres avec 0 echec.

### Temporisation et User-Agent

Temporisation et User-Agent documentes le 2026-09-07.

- `ROBOTSTXT_OBEY=True` est conserve pour rester sur le comportement standard de
  Scrapy.
- `USER_AGENT` identifie explicitement le projet.
- `DOWNLOAD_DELAY=0.5` applique une pause fixe entre les requetes vers le meme
  domaine.
- `RANDOMIZE_DOWNLOAD_DELAY=False` rend le rythme plus previsible d'un lancement
  a l'autre.
- `CONCURRENT_REQUESTS_PER_DOMAIN=1` limite la charge envoyee au site et
  simplifie le raisonnement pour un projet debutant.
- Les commandes rejouables sont documentees dans le README avec l'option `-O`.
- Validation locale : les reglages sont couverts par `tests/test_settings.py`.
- Validation reseau : un crawl `limit=3` a exporte 3 livres avec 0 echec et a
  confirme les reglages charges par Scrapy.

### Correction des exports

Correction realisee le 2026-09-07.

- Trois exports distincts sont documentes : liste, sample detaille, final
  detaille.
- Les commandes d'export utilisent `-O` pour remplacer proprement le fichier
  cible.
- Un validateur independant du scraping est ajoute :
  `uv run python -m books_catalog_scraper.validate_exports --sample`.
- Le mode `--full` validera `exports/books_details.json` quand le full scrape
  aura ete lance.
- Le validateur controle les champs obligatoires, types, URLs, ratings, stocks,
  avis, categories, prix, UPC et la coherence des URLs entre phase 1 et phase 2.
- Validation locale : tests unitaires ajoutes et couverture maintenue a 100%.

### Gestion des erreurs

Gestion des erreurs realisee le 2026-09-07.

- Parametre ajoute sur les spiders : `max_errors`.
- Valeur par defaut : `50`.
- Une carte ou une fiche invalide est journalisee puis ignoree.
- Si le seuil est depasse, Scrapy ferme le spider avec une raison explicite,
  par exemple `max_errors_exceeded_51`.
- Les doublons d'URL restent journalises separement et ne comptent pas comme
  erreurs de parsing.
- Les commandes README documentent des seuils explicites pour reproduire les
  memes conditions de lancement.
- Validation locale : tests ajoutes pour le seuil, le parseur de parametre et
  l'arret explicite.
- Validation reseau : `limit=3` avec `max_errors=5` a exporte 3 livres avec 0
  echec.

### Reprise apres interruption

Reprise apres interruption realisee le 2026-09-07.

- La reprise repose sur `books.upc` et `ON CONFLICT (upc) DO UPDATE`.
- Chaque item sauvegarde est committe immediatement.
- Relancer la meme commande ne cree pas de doublons.
- Le crawler reparcourt les pages depuis le debut, ce qui reste acceptable pour
  le brief.
- Les commandes de demonstration et de verification SQL sont documentees.
- Validation PostgreSQL reelle : apres relance de `limit=3`, la base contient 3
  livres, 0 doublon UPC et 0 doublon URL produit.

### Chargement PostgreSQL

Chargement PostgreSQL realise le 2026-09-07.

- Pipeline ajoute : `PostgresPipeline`.
- Activation explicite : `-s POSTGRES_ENABLED=true`.
- Le pipeline est desactive par defaut pour ne pas imposer PostgreSQL lors des
  exports JSON.
- Les categories sont inserees ou mises a jour par nom.
- Les livres sont inserees ou mises a jour avec `ON CONFLICT (upc) DO UPDATE`.
- La cle retenue est l'UPC, pas le titre.
- Un `commit` est fait apres chaque item.
- Validation locale : tests unitaires du pipeline, de la configuration `.env` et
  des requetes d'upsert.
- Validation PostgreSQL reelle : un echantillon `limit=3` a sauvegarde 3 livres
  et 3 categories, avec 0 doublon UPC apres relance.

### Script de chargement

Script de chargement realise le 2026-09-07.

- Script ajoute : `scripts/load_books.py`.
- Commande sample :
  `uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample`.
- Commande finale :
  `uv run python -m scripts.load_books --input exports/books_details.json`.
- Le script valide l'export avant chargement.
- Il reutilise les memes upserts que le pipeline Scrapy.
- Validation locale : tests unitaires ajoutes et `scripts` inclus dans la
  couverture.
- Validation PostgreSQL reelle : relance du script sur
  `exports/books_details_sample.json`, 20 livres en base et 0 doublon UPC.

### Exports

Exports documentes le 2026-09-07.

- Export phase 1 : `exports/books_list.json`.
- Export sample detaille : `exports/books_details_sample.json`.
- Export final attendu : `exports/books_details.json`.
- Les commandes utilisent `-O` pour rendre la regeneration des fichiers
  rejouable.
- Les prix restent des chaines JSON pour conserver les valeurs exactes.
- Le sample sert a tester et demontrer le projet, mais ne remplace pas le
  livrable final.
- Validation locale : le validateur `--sample` controle l'export de liste et le
  sample detaille.
- Le full scrape et la validation `--full` restent a lancer pour produire le
  livrable final complet.

## Blocages rencontres

A completer au fil du projet.
