# Roadmap de realisation du brief

Cette roadmap suit le brief `brief.md` et garde une approche simple a relire
pour un niveau debutant-intermediaire en Scrapy.

## 1. Socle projet

Etat attendu :

- projet Python gere avec UV ;
- Scrapy installe ;
- PostgreSQL lance avec Docker Compose ;
- fichier `.env.example` fourni ;
- script SQL de creation de base dans `db/schema.sql` ;
- documentation minimale dans `README.md` et `docs/`.

Ce socle ne contient pas encore de spider, de pipeline ou de logique de scraping.

## 2. Reconnaissance du site

Avant d'ecrire le scraper de production :

- consulter `https://books.toscrape.com/robots.txt` ;
- noter ce que le fichier autorise ;
- observer la pagination du catalogue ;
- verifier si les URLs de pagination sont previsibles ou suivies via `next` ;
- compter les pages de liste attendues ;
- verifier si le site annonce le nombre total de resultats ;
- observer les liens vers les fiches produit ;
- noter que les URLs produit sont relatives ;
- verifier deux ou trois fiches produit ;
- reperer les champs absents des pages de liste.

Documentation a completer :

- `docs/journal-de-bord.md` ;
- `docs/fonctionnement.md`.

## 3. Collecteur des pages de liste

Creer un spider Scrapy simple, par exemple `books_list`.

Objectif :

- parcourir les pages de liste du catalogue ;
- suivre le lien `next` plutot que concatener les URLs manuellement ;
- extraire pour chaque livre :
  - titre ;
  - prix affiche sur la liste ;
  - note ;
  - URL absolue de la fiche produit.

Point important :

- la note est dans une classe CSS, par exemple `star-rating Three` ;
- elle doit etre convertie en nombre entier.

Commande cible :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
```

Resultat attendu en fin de J1 :

- un fichier contenant les 1 000 livres avec leur URL de fiche ;
- des logs indiquant combien de pages ont ete parcourues.

## 4. Collecteur des fiches produit

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

## 5. Mode echantillon

Ajouter un parametre au spider complet :

```bash
uv run scrapy crawl books_details -a limit=20
```

Objectifs :

- faciliter les tests ;
- faciliter la demonstration ;
- eviter une collecte complete a chaque essai.

Le parametre `limit` doit limiter le nombre de fiches produit visitees.

## 6. Temporisation et User-Agent

Configurer Scrapy simplement :

- `USER_AGENT` explicite ;
- `DOWNLOAD_DELAY` raisonnable ;
- `ROBOTSTXT_OBEY = True` ;
- concurrence limitee par domaine.

La justification du rythme choisi doit etre ajoutee dans la documentation.

Principe recommande :

- aller assez lentement pour ne pas envoyer trop de requetes en parallele ;
- rester assez rapide pour collecter 1 000 fiches dans un temps acceptable.

## 7. Gestion des erreurs

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

## 8. Stockage PostgreSQL

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

## 9. Reprise apres interruption

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

## 10. Script de chargement

Le brief demande un script de creation de la base et un script de chargement.

Le script de creation existe dans :

```text
db/schema.sql
```

Ajouter ensuite un script de chargement, par exemple :

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

## 11. Exports

Prevoir au minimum :

- `exports/books_list.json` pour la fin de J1 ;
- `exports/books_details.json` pour le resultat final.

Les exports doivent etre simples a ouvrir et a verifier.

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
- `docs/installation.md` ;
- `docs/fonctionnement.md` ;
- `docs/environnement.md` ;
- `docs/journal-de-bord.md` ;
- `docs/observations-prix-taxe.md`.

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
