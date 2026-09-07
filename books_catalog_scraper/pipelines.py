import logging

from scrapy.exceptions import NotConfigured

from books_catalog_scraper.postgres import connect_postgres, upsert_book

logger = logging.getLogger(__name__)


class PostgresPipeline:
    def __init__(self) -> None:
        self.connection = None
        self.books_saved = 0

    @classmethod
    def from_crawler(cls, crawler):
        if not crawler.settings.getbool("POSTGRES_ENABLED", False):
            raise NotConfigured("Pipeline PostgreSQL desactive")
        return cls()

    def open_spider(self) -> None:
        self.connection = connect_postgres()
        logger.info("Pipeline PostgreSQL active")

    def close_spider(self) -> None:
        if self.connection is None:
            return

        self.connection.close()
        logger.info("%s livres sauvegardes dans PostgreSQL", self.books_saved)

    def process_item(self, item: dict) -> dict:
        if self.connection is None:
            raise RuntimeError("Connexion PostgreSQL non initialisee")

        try:
            upsert_book(self.connection, item)
        except Exception:
            self.connection.rollback()
            raise

        self.connection.commit()
        self.books_saved += 1
        return item
