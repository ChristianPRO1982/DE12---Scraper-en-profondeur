# Roadmap de realisation du brief

Cette roadmap suit le brief `brief.md` et garde une approche simple a relire
pour un niveau debutant-intermediaire en Scrapy.

## 1. Socle projet

Statut : realise.

Etat attendu :

- projet Python gere avec UV : `pyproject.toml`, `uv.lock` et `uv.toml` ;
- Scrapy installe : dependance declaree et projet chargeable via `scrapy.cfg` ;
- PostgreSQL prepare avec Docker Compose : `compose.yaml` ;
- fichier `.env.example` fourni ;
- script SQL de creation de base dans `db/schema.sql` ;
- documentation minimale dans `README.md` et `docs/` ;
- qualite preparee avec Ruff, Pytest et Coverage.

Le socle initial ne contenait pas encore de spider, de pipeline ou de logique de
scraping. Les spiders sont ajoutes dans les etapes suivantes de cette roadmap.

Commandes de verification du socle :

```bash
uv sync
uv run scrapy list
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
docker compose --env-file .env.example config
```

## 2. Reconnaissance du site

Statut : realise.

Avant d'ecrire le scraper de production :

- consulter `https://books.toscrape.com/robots.txt` : fait, reponse HTTP 404 ;
- repondre a la question du brief sur ce qu'il autorise : aucun `robots.txt`
  n'est publie, donc aucune directive technique `Disallow` ou `Crawl-delay`
  n'existe sur ce point ;
- verifier s'il existe une politique equivalente : aucune politique formalisee
  identifiee sur Books to Scrape ;
- noter le contexte officiel : le site indique explicitement etre destine au
  scraping ;
- observer la pagination du catalogue : fait ;
- verifier si les URLs de pagination sont previsibles ou suivies via `next` :
  lien `next` present, a suivre avec Scrapy ;
- compter les pages de liste attendues : 50 pages ;
- verifier si le site annonce le nombre total de resultats : 1 000 resultats ;
- observer les liens vers les fiches produit : fait ;
- noter que les URLs produit sont relatives : fait ;
- verifier deux ou trois fiches produit : fait ;
- reperer les champs absents des pages de liste : fait.

Documentation a completer :

- `docs/09-livrable-journal-de-bord.md` : complete ;
- `docs/03-preparation-fonctionnement.md` : complete ;
- `docs/05-phase-1-reconnaissance.md` : ajoute.

## 3. Collecteur des pages de liste

Statut : realise.

Creer un spider Scrapy simple, par exemple `books_list`.

Objectif :

- parcourir les pages de liste du catalogue ;
- suivre le lien `next` plutot que concatener les URLs manuellement ;
- extraire pour chaque livre :
  - titre ;
  - prix affiche sur la liste sous le champ `price_list` ;
  - note ;
  - URL absolue de la fiche produit.

Point important :

- la note est dans une classe CSS, par exemple `star-rating Three` ;
- elle doit etre convertie en nombre entier.
- le prix est converti avec `Decimal`, pas avec `float`.
- une carte produit invalide est journalisee et ignoree au lieu d'arreter toute
  la page.

Commande cible :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
```

Resultat attendu en fin de J1 :

- un fichier contenant les 1 000 livres avec leur URL de fiche : fait,
  `exports/books_list.json` ;
- des logs indiquant combien de pages ont ete parcourues : fait, 50 pages.

Documentation :

- `docs/06-phase-1-collecteur-pages-liste.md` : ajoute ;
- `docs/09-livrable-journal-de-bord.md` : complete.

## 4. Collecteur des fiches produit

Statut : realise.

Creer un spider Scrapy complet, par exemple `books_details`.

Objectif :

- partir des pages de liste ;
- visiter chaque fiche produit ;
- extraire les champs finaux :
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
  - URL image si utile.

Commencer par un seul livre :

- enrichir un livre de bout en bout ;
- comparer les valeurs obtenues avec la fiche affichee dans le navigateur ;
- corriger les selecteurs avant de passer a l'echelle.

Resultat obtenu :

- spider cree : `books_details` ;
- extraction par libelle de la table `Product Information` ;
- categorie extraite du fil d'Ariane ;
- stock reel extrait depuis la fiche produit ;
- UPC extrait pour servir de future cle de reprise ;
- prix convertis avec `Decimal` ;
- erreurs de carte ou de fiche journalisees puis ignorees ;
- tests unitaires et tests spider ajoutes ;
- validation reseau courte realisee sur fiches reelles.

Commande cible :

```bash
uv run scrapy crawl books_details -O exports/books_details.json
```

Documentation :

- `docs/07-phase-2-collecteur-fiches-produit.md` : ajoute ;
- `docs/09-livrable-journal-de-bord.md` : complete.

## 5. Mode echantillon

Statut : realise.

Ajouter un parametre au spider complet :

```bash
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
```

Objectifs :

- faciliter les tests ;
- faciliter la demonstration ;
- eviter une collecte complete a chaque essai.

Le parametre `limit` doit limiter le nombre de fiches produit visitees.

Resultat obtenu :

- parametre Scrapy `limit` ajoute au spider `books_details` ;
- `limit=20` programme au maximum 20 fiches produit ;
- la pagination s'arrete quand la limite est atteinte ;
- une limite vide garde le comportement complet ;
- une limite inferieure a 1 est rejetee ;
- tests ajoutes ;
- validation reseau realisee avec 20 livres exportes et 0 echec.

Commande rejouable documentee dans le README :

```bash
uv run scrapy crawl books_details -a limit=20 -O exports/books_details_sample.json
```

L'option `-O` ecrase l'ancien export et evite un nettoyage manuel.

## 6. Temporisation et User-Agent

Statut : realise.

Configurer Scrapy simplement :

- `USER_AGENT` explicite ;
- `DOWNLOAD_DELAY` raisonnable ;
- `ROBOTSTXT_OBEY = True` ;
- concurrence limitee par domaine.

La justification du rythme choisi doit etre ajoutee dans la documentation.

Principe recommande :

- aller assez lentement pour ne pas envoyer trop de requetes en parallele ;
- rester assez rapide pour collecter 1 000 fiches dans un temps acceptable.

Resultat obtenu :

- `ROBOTSTXT_OBEY=True` ;
- `USER_AGENT` explicite ;
- `DOWNLOAD_DELAY=0.5` ;
- `RANDOMIZE_DOWNLOAD_DELAY=False` pour eviter une temporisation aleatoire ;
- `CONCURRENT_REQUESTS_PER_DOMAIN=1` pour garder une collecte simple,
  rejouable et peu agressive ;
- commandes rejouables documentees dans le README avec `-O`.

Documentation :

- `docs/08-phase-2-temporisation-user-agent.md` : ajoute ;
- `README.md` : commandes et reglages ajoutes.

## Correction. Validation des exports

Statut : realise.

Objectif :

- conserver trois exports distincts ;
- rendre les commandes d'export rejouables avec `-O` ;
- valider automatiquement les fichiers JSON avant le full scrape et avant le
  chargement PostgreSQL ;
- refuser clairement un export incomplet ou incoherent.

Commandes :

```bash
uv run python -m books_catalog_scraper.validate_exports --sample
uv run python -m books_catalog_scraper.validate_exports --full
```

Resultat obtenu :

- validateur independant du scraping ;
- controle du schema `books_list.json` ;
- controle du schema detaille commun au sample et au final ;
- controle des types, URLs, ratings, stocks, avis, categories, prix et UPC ;
- comparaison des URLs et des titres entre phase 1 et phase 2 ;
- statistiques prix/taxe affichees ;
- code retour non nul en cas d'erreur bloquante ;
- tests unitaires ajoutes.

Documentation :

- `docs/11-correction-validation-exports.md` : ajoute ;
- `README.md` : commandes de validation ajoutees.

## 7. Gestion des erreurs

Statut : realise.

Le scraper ne doit pas tomber pour une fiche isolee.

Comportement attendu :

- journaliser les fiches en erreur ;
- ignorer une fiche dont la structure est inattendue ;
- continuer la collecte ;
- arreter seulement si trop d'erreurs indiquent que le site a probablement change.

Approche simple :

- definir un seuil d'erreurs maximal ;
- garder les conversions dans des fonctions courtes :
  - `parse_price` ;
  - `parse_rating` ;
  - `parse_stock` ;
  - `parse_int`.

Resultat obtenu :

- les spiders `books_list` et `books_details` acceptent `max_errors` ;
- la valeur par defaut est `50` ;
- une erreur de parsing incremente `failed_products` ;
- une carte ou une fiche invalide est journalisee puis ignoree tant que le seuil
  n'est pas depasse ;
- si le seuil est depasse, Scrapy ferme le spider avec une raison explicite,
  par exemple `max_errors_exceeded_51` ;
- les doublons d'URL restent journalises et ignores sans compter comme erreur de
  parsing ;
- tests dedies ajoutes.

Commandes rejouables :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
```

Documentation :

- `docs/12-phase-2-gestion-erreurs.md` : ajoute ;
- `README.md` : commandes avec `max_errors` ajoutees.

## 8. Stockage PostgreSQL

Statut : realise.

Utiliser le schema `db/schema.sql`.

Tables principales :

- `categories` ;
- `books`.

Choix de cle :

- utiliser `books.upc` comme cle primaire ;
- ne pas utiliser le titre comme cle, car le brief indique qu'il n'est pas fiable.

Chargement attendu :

- inserer ou retrouver la categorie ;
- inserer le livre ;
- utiliser `ON CONFLICT (upc) DO UPDATE` pour eviter les doublons.

Resultat obtenu :

- pipeline Scrapy optionnel `PostgresPipeline` ;
- pipeline desactive par defaut pour conserver les exports JSON sans base ;
- activation explicite avec `-s POSTGRES_ENABLED=true` ;
- lecture de la configuration depuis `.env` ou l'environnement ;
- insertion/upsert des categories ;
- insertion/upsert des livres avec `books.upc` comme cle ;
- `commit` apres chaque item ;
- tests unitaires sans dependance a une base reelle ;
- validation PostgreSQL reelle sur un echantillon de 3 livres.

Commandes rejouables :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -s POSTGRES_ENABLED=true -O exports/books_details_sample.json
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

Documentation :

- `docs/13-phase-2-stockage-postgresql.md` : ajoute ;
- `README.md` : commandes PostgreSQL ajoutees.

## 9. Reprise apres interruption

Statut : realise.

La reprise est obligatoire.

Solution simple et demonstrable :

- ecrire chaque livre en base des qu'il est extrait ;
- utiliser `upc` comme cle primaire ;
- utiliser un upsert PostgreSQL ;
- a la relance, les livres deja collectes sont mis a jour au lieu d'etre dupliques.

Demonstration attendue :

- lancer le scraper en mode echantillon ou collecte longue ;
- interrompre volontairement ;
- relancer la meme commande ;
- verifier que la base ne contient pas de doublons.

Resultat obtenu :

- reprise basee sur l'upsert PostgreSQL ;
- `books.upc` utilise comme cle primaire ;
- `commit` apres chaque item ;
- relance de la meme commande sans duplication ;
- verification SQL des doublons UPC documentee ;
- validation PostgreSQL reelle apres relance : 3 livres, 0 doublon UPC, 0
  doublon URL produit ;
- limite assumee : le crawler reparcourt les pages depuis le debut, mais les
  lignes deja presentes sont mises a jour.

Commandes rejouables :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -s POSTGRES_ENABLED=true -O exports/books_details_sample.json
uv run scrapy crawl books_details -a max_errors=50 -s POSTGRES_ENABLED=true -O exports/books_details.json
```

Documentation :

- `docs/14-phase-2-reprise-apres-interruption.md` : ajoute ;
- `README.md` : commandes de reprise et verification doublons ajoutees.

## 10. Script de chargement

Statut : realise.

Le brief demande un script de creation de la base et un script de chargement.

Le script de creation existe dans :

```text
db/schema.sql
```

Script de chargement ajoute :

```text
scripts/load_books.py
```

Role du script :

- lire un export JSON ou CSV ;
- inserer les categories ;
- inserer les livres ;
- utiliser les memes regles d'upsert que le pipeline.

Le pipeline Scrapy peut etre utilise pour le chargement direct, mais le script de
chargement separe reste utile comme livrable explicite du brief.

Resultat obtenu :

- script lanceable avec `uv run python -m scripts.load_books` ;
- chargement d'un export JSON detaille ;
- validation de l'export avant chargement ;
- mode sample explicite avec `--allow-sample` ;
- mode final strict avec 1 000 fiches attendues ;
- reutilisation de `upsert_book` ;
- `commit` apres chaque livre ;
- script inclus dans la couverture de tests ;
- validation PostgreSQL reelle sur `exports/books_details_sample.json` relancee
  sans doublon UPC.

Commandes rejouables :

```bash
uv run python -m scripts.load_books --input exports/books_details_sample.json --allow-sample
uv run python -m scripts.load_books --input exports/books_details.json
```

Documentation :

- `docs/15-phase-2-script-chargement.md` : ajoute ;
- `README.md` : commandes de chargement separe ajoutees.

## 11. Exports

Statut : realise.

Exports conserves :

- `exports/books_list.json` pour la fin de J1 ;
- `exports/books_details_sample.json` pour les demonstrations et tests rapides ;
- `exports/books_details.json` pour le resultat final.

Resultat obtenu :

- les exports JSON sont produits via Scrapy avec `-O` ;
- relancer une commande remplace le fichier cible ;
- le sample garde le meme schema que le final ;
- `books_list.json` est valide avec 1 000 livres attendus ;
- `books_details_sample.json` est valide sans exiger 1 000 fiches ;
- `books_details.json` est reserve au full scrape final ;
- le validateur `--full` controle les 1 000 fiches, les UPC uniques et la
  coherence avec l'export de liste.

Commandes rejouables :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
uv run python -m books_catalog_scraper.validate_exports --sample
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
uv run python -m books_catalog_scraper.validate_exports --full
```

Documentation :

- `docs/16-phase-2-exports.md` : ajoute ;
- `README.md` : section exports ajoutee.

## 12. Requetes de demonstration

Preparer des requetes SQL pour repondre a la question centrale :

```sql
SELECT *
FROM books_stock_alerts
ORDER BY stock_quantity ASC, rating DESC;
```

```sql
SELECT *
FROM books_best_rated
ORDER BY rating DESC, review_count DESC, title ASC;
```

```sql
SELECT COUNT(*) AS total_books
FROM books;
```

```sql
SELECT upc, COUNT(*)
FROM books
GROUP BY upc
HAVING COUNT(*) > 1;
```

## 13. Documentation finale

Mettre a jour :

- `README.md` ;
- `docs/01-preparation-installation.md` ;
- `docs/02-preparation-environnement.md` ;
- `docs/03-preparation-fonctionnement.md` ;
- `docs/04-preparation-qualite.md` ;
- `docs/05-phase-1-reconnaissance.md` ;
- `docs/06-phase-1-collecteur-pages-liste.md` ;
- `docs/07-phase-2-collecteur-fiches-produit.md` ;
- `docs/08-phase-2-temporisation-user-agent.md` ;
- `docs/09-livrable-journal-de-bord.md` ;
- `docs/10-livrable-observations-prix-taxe.md` ;
- `docs/11-correction-validation-exports.md` ;
- `docs/12-phase-2-gestion-erreurs.md` ;
- `docs/13-phase-2-stockage-postgresql.md` ;
- `docs/14-phase-2-reprise-apres-interruption.md` ;
- `docs/15-phase-2-script-chargement.md` ;
- `docs/16-phase-2-exports.md`.

La documentation finale doit expliquer :

- installation depuis zero ;
- lancement de PostgreSQL ;
- creation du schema ;
- lancement du scraper de liste ;
- lancement du scraper complet ;
- mode echantillon ;
- reprise apres interruption ;
- requetes SQL de demonstration ;
- choix de l'UPC comme cle ;
- justification du User-Agent et de la temporisation.

## 14. Validation finale

Scenario de validation :

```bash
cp .env.example .env
uv sync
docker compose up -d
docker compose exec postgres sh -c 'psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f /app/db/schema.sql'
uv run scrapy crawl books_details -a limit=20
```

Puis :

- verifier les logs ;
- verifier le contenu PostgreSQL ;
- interrompre et relancer le scraper ;
- verifier l'absence de doublons ;
- lancer la collecte complete ;
- verifier que les 1 000 livres sont presents en base ;
- verifier que les champs obligatoires sont remplis.

## 15. Principes de code

Le code doit rester robuste mais lisible :

- peu de fichiers ;
- noms explicites ;
- fonctions courtes ;
- pas d'ORM ;
- pas de framework de migration ;
- SQL simple ;
- logs comprehensibles ;
- exceptions ciblees ;
- pas d'abstraction avancee inutile.
