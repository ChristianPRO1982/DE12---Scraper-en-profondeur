# 12 - Phase 2 - Gestion des erreurs

Partie du brief liee : robustesse du scraper, erreurs visibles et reprise
rejouable des commandes.

## Objectif

Le scraper ne doit pas tomber pour une seule carte ou une seule fiche mal
formee.

Il doit :

- journaliser l'erreur ;
- ignorer l'element invalide ;
- continuer la collecte ;
- arreter clairement le crawl si le nombre d'erreurs indique un probleme plus
  large.

## Parametre max_errors

Les spiders `books_list` et `books_details` acceptent le parametre Scrapy
`max_errors`.

Valeur par defaut :

```text
max_errors=50
```

Le crawl s'arrete quand le nombre d'erreurs depasse ce seuil.

Exemple echantillon :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
```

Exemple collecte complete :

```bash
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
```

## Rejouabilite

Le seuil est passe dans la commande. Un meme lancement peut donc etre reproduit
avec les memes conditions.

L'option `-O` remplace l'export precedent et evite les fichiers JSON contenant
plusieurs collectes accumulees.

## Erreurs gerees

Les erreurs suivantes sont visibles dans les logs et comptabilisees :

- carte produit de liste incomplete ;
- note CSS inconnue ;
- prix invalide ;
- fiche produit sans champ obligatoire ;
- categorie introuvable ;
- stock reel impossible a extraire ;
- nombre d'avis invalide.

Les doublons d'URL sont aussi journalises et ignores, mais ils ne comptent pas
comme erreur de parsing.

## Arret explicite

Si le seuil est depasse, Scrapy ferme le spider avec une raison du type :

```text
max_errors_exceeded_51
```

Cela rend un run incomplet visible dans les logs.

## Verification

Tests dedies :

```bash
uv run pytest -q tests/test_error_policy.py
```

Validation reseau courte realisee :

```bash
uv run scrapy crawl books_details -a limit=3 -a max_errors=5 -O /tmp/books_details_errors_sample.json
```

Resultat :

- 3 fiches programmees ;
- 3 livres exportes ;
- 0 echec ;
- fermeture normale du spider.

Chaine complete :

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
uv run coverage run -m pytest && uv run coverage report -m
```
