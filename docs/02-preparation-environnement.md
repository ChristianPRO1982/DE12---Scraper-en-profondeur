# 02 - Preparation - Variables d'environnement

Partie du brief liee : preparation du socle technique et lancement local.

Le fichier `.env` contient la configuration locale. Il ne doit pas etre commite.

Pour demarrer :

```bash
cp .env.example .env
```

## PostgreSQL

- `POSTGRES_DB` : nom de la base creee par l'image Docker PostgreSQL.
- `POSTGRES_USER` : utilisateur applicatif PostgreSQL.
- `POSTGRES_PASSWORD` : mot de passe de l'utilisateur PostgreSQL.
- `POSTGRES_HOST` : hote utilise depuis les scripts Python. En local, garder
  `localhost`.
- `POSTGRES_PORT` : port expose sur la machine locale.

## Scrapy

Le User-Agent et la temporisation Scrapy sont configures dans
`books_catalog_scraper/settings.py`, car ce sont des reglages propres au crawler.
Ils sont justifies dans
[08-phase-2-temporisation-user-agent.md](08-phase-2-temporisation-user-agent.md).
