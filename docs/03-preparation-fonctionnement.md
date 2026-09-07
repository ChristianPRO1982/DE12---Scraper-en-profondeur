# 03 - Preparation - Fonctionnement prevu

Partie du brief liee : vue d'ensemble du fonctionnement attendu, phase 1,
phase 2 et stockage PostgreSQL.

Le projet suivra les deux phases du brief.

## Reconnaissance

La reconnaissance du site est documentee dans
[05-phase-1-reconnaissance.md](05-phase-1-reconnaissance.md).

Points structurants :

- aucune politique de crawling formalisee identifiee ;
- `robots.txt` absent, reponse HTTP 404 ;
- site explicitement presente comme un bac a sable de scraping ;
- 1 000 livres annonces ;
- 20 livres par page ;
- 50 pages de liste ;
- pagination par lien `next` ;
- liens produit relatifs ;
- stock reel et UPC presents uniquement sur les fiches produit.

## Phase 1

Le collecteur de pages de liste devra parcourir les pages du catalogue Books to
Scrape et produire, pour chaque livre :

- titre ;
- prix affiche sur la liste sous le champ `price_list` ;
- note numerique convertie depuis la classe CSS ;
- URL de la fiche produit.

Statut : realise avec le spider `books_list`.

Commande :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
```

Documentation detaillee :

- [06-phase-1-collecteur-pages-liste.md](06-phase-1-collecteur-pages-liste.md)

## Phase 2

Le collecteur de fiches produit visite chaque fiche et enrichit les donnees
avec :

- UPC ;
- titre ;
- URL produit ;
- categorie ;
- note numerique ;
- prix de liste ;
- prix hors taxe ;
- prix TTC ;
- taxe ;
- stock reel ;
- nombre d'avis ;
- description ;
- URL image.

Statut : realise avec le spider `books_details`.

Commande :

```bash
uv run scrapy crawl books_details -O exports/books_details.json
```

Commande echantillon rejouable :

```bash
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
```

Documentation detaillee :

- [07-phase-2-collecteur-fiches-produit.md](07-phase-2-collecteur-fiches-produit.md)
- [08-phase-2-temporisation-user-agent.md](08-phase-2-temporisation-user-agent.md)

## Temporisation et User-Agent

Statut : realise.

Le scraper utilise un User-Agent explicite et une temporisation fixe :

- `ROBOTSTXT_OBEY=True` ;
- `USER_AGENT=DE12-books-scraper/0.1 (...)` ;
- `DOWNLOAD_DELAY=0.5` ;
- `RANDOMIZE_DOWNLOAD_DELAY=False` ;
- `CONCURRENT_REQUESTS_PER_DOMAIN=1`.

Ces choix rendent les commandes plus rejouables et limitent la charge envoyee au
site.

## Gestion des erreurs

Statut : realise.

Les spiders `books_list` et `books_details` acceptent un seuil `max_errors`.

Exemple :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
```

Une carte ou une fiche invalide est journalisee puis ignoree. Si le nombre
d'erreurs depasse le seuil, Scrapy ferme le spider avec une raison explicite.

Documentation detaillee :

- [12-phase-2-gestion-erreurs.md](12-phase-2-gestion-erreurs.md)

## Reprise apres interruption

Statut : realise.

La reprise est effective via PostgreSQL. La cle fonctionnelle retenue est l'UPC,
car le brief indique que le titre n'est pas une cle fiable.

Chaque item est committe apres son upsert. En cas d'interruption, les livres
deja sauvegardes restent en base. A la relance, ils sont mis a jour au lieu
d'etre dupliques.

Documentation detaillee :

- [14-phase-2-reprise-apres-interruption.md](14-phase-2-reprise-apres-interruption.md)

## Base de donnees

PostgreSQL est lance par Docker Compose.

Le schema est cree par [../db/schema.sql](../db/schema.sql). Il contient :

- `categories` : les categories du catalogue ;
- `books` : les livres collectes, avec `upc` comme cle primaire ;
- `books_catalog` : vue de lecture avec le nom de categorie ;
- `books_stock_alerts` : vue des livres en rupture ou en stock faible ;
- `books_best_rated` : vue des livres notes 4 ou 5.

Il n'y a pas de table intermediaire. Le pipeline insere directement les
categories et les livres, puis utilise `ON CONFLICT` sur `books.upc` pour rendre
les executions successives idempotentes.

Statut : realise avec le pipeline `PostgresPipeline`.

Commande echantillon avec stockage :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -s POSTGRES_ENABLED=true -O exports/books_details_sample.json
```

Commande complete avec stockage :

```bash
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

Documentation detaillee :

- [13-phase-2-stockage-postgresql.md](13-phase-2-stockage-postgresql.md)

## Script de chargement

Statut : realise.

Le script `scripts.load_books` charge un export JSON detaille sans relancer le
scraping.

Commande sample :

```bash
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
```

Commande finale :

```bash
uv run python -m scripts.load_books --input exports/books_details.json
```

Documentation detaillee :

- [15-phase-2-script-chargement.md](15-phase-2-script-chargement.md)
