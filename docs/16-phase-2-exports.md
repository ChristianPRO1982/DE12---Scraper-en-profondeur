# 16 - Phase 2 - Exports

Partie du brief liee : livrables JSON/CSV, verification des donnees collectees
et resultat final exploitable.

## Objectif

Les exports doivent etre simples a produire, simples a ouvrir et rejouables sans
nettoyage manuel.

Le projet conserve trois fichiers distincts :

- `exports/books_list.json` : export de phase 1, attendu a 1 000 livres ;
- `exports/books_details_sample.json` : export de demonstration limite, meme
  schema que le final ;
- `exports/books_details.json` : export final, attendu a 1 000 fiches produit.

Le sample ne remplace jamais l'export final. Il sert uniquement aux essais
rapides, aux demonstrations et au chargement PostgreSQL en petit volume.

## Rejouabilite

Toutes les commandes d'export utilisent l'option Scrapy `-O`.

Cette option ecrase le fichier cible avant d'ecrire le nouvel export. Elle evite
d'accumuler des objets JSON d'anciennes executions.

Ne pas utiliser `-o` pour ces livrables, car cette option peut ajouter au fichier
existant selon le format et rendre la verification moins claire.

## Commandes

Export des pages de liste :

```bash
uv run scrapy crawl books_list -O exports/books_list.json
```

Export d'un echantillon detaille :

```bash
uv run scrapy crawl books_details -a limit=20 -a max_errors=5 -O exports/books_details_sample.json
```

Validation de l'echantillon :

```bash
uv run python -m books_catalog_scraper.validate_exports --sample
```

Export final des fiches produit :

```bash
uv run scrapy crawl books_details -a max_errors=50 -O exports/books_details.json
```

Validation finale :

```bash
uv run python -m books_catalog_scraper.validate_exports --full
```

## Schema attendu

`exports/books_list.json` contient les champs de phase 1 :

- `title` ;
- `price_list` ;
- `rating` ;
- `product_url`.

Les exports detaillees contiennent le schema final :

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

Les prix restent exportes en chaines JSON pour conserver les valeurs decimales
exactes produites cote Python avec `Decimal`.

## Verification

Le validateur est independant du scraping. Il peut donc etre relance autant de
fois que necessaire sans modifier les donnees.

Le mode `--sample` controle :

- `exports/books_list.json` ;
- `exports/books_details_sample.json`.

Le mode `--full` controle :

- `exports/books_list.json` ;
- `exports/books_details.json` ;
- les 1 000 objets attendus ;
- les 1 000 UPC uniques ;
- la coherence des URLs et des titres entre la phase 1 et la phase 2.

Etat actuel du projet :

- `exports/books_list.json` existe et correspond a l'export de phase 1 ;
- `exports/books_details_sample.json` existe et sert de sample rejouable ;
- `exports/books_details.json` reste a produire lors du full scrape final.
