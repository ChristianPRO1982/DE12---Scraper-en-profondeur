# Qualite du code

Le projet utilise Ruff pour le style et les erreurs simples, Pytest pour les
tests, et Coverage pour mesurer la couverture.

## Commandes habituelles

Verifier le lint, le formatage et les tests :

```bash
uv run ruff check . && uv run ruff format --check . && uv run pytest -q
```

Verifier la couverture :

```bash
uv run coverage run -m pytest && uv run coverage report -m
```

Formater le code :

```bash
uv run ruff format .
```

## Regle de couverture

La couverture minimale est configuree a 100% dans `pyproject.toml`.

Cette regle force chaque nouvelle fonction utile du scraper a etre testee. Elle
sera surtout importante pour les fonctions de parsing :

- conversion des prix ;
- conversion des notes depuis les classes CSS ;
- extraction du stock reel ;
- extraction du nombre d'avis.
