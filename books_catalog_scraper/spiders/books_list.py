from collections.abc import Iterator

import scrapy
from scrapy import Request, Selector
from scrapy.exceptions import CloseSpider

from books_catalog_scraper.error_policy import has_exceeded_error_limit, parse_max_errors
from books_catalog_scraper.extractors import extract_list_book


class BooksListSpider(scrapy.Spider):
    name = "books_list"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def __init__(
        self, max_errors: str | int | None = None, *args: object, **kwargs: object
    ) -> None:
        super().__init__(*args, **kwargs)
        self.max_errors = parse_max_errors(max_errors)
        self.pages_seen = 0
        self.books_seen = 0
        self.failed_products = 0
        self.duplicate_product_urls = 0
        self.product_urls_seen: set[str] = set()

    def parse(self, response: scrapy.http.Response) -> Iterator[dict | Request]:
        self.pages_seen += 1

        products = response.css("article.product_pod")
        self.logger.info(
            "Page de liste parcourue: %s (%s livres trouves)",
            response.url,
            len(products),
        )

        for product in products:
            try:
                book = self.parse_book(product, response)
            except ValueError as error:
                self.record_failure()
                self.logger.warning(
                    "Livre ignore sur %s: %s",
                    response.url,
                    error,
                )
                continue

            product_url = book["product_url"]
            if product_url in self.product_urls_seen:
                self.duplicate_product_urls += 1
                self.logger.warning("URL produit dupliquee ignoree: %s", product_url)
                continue

            self.product_urls_seen.add(product_url)
            self.books_seen += 1
            yield book

        next_url = response.css("li.next a::attr(href)").get()
        if next_url:
            yield response.follow(next_url, callback=self.parse)
        else:
            self.logger.info(
                (
                    "Collecte des pages de liste terminee: "
                    "%s pages parcourues, %s livres exportes, "
                    "%s livres ignores, %s doublons URL ignores"
                ),
                self.pages_seen,
                self.books_seen,
                self.failed_products,
                self.duplicate_product_urls,
            )

    def parse_book(self, product: Selector, response: scrapy.http.Response) -> dict:
        return extract_list_book(product, response)

    def record_failure(self) -> None:
        self.failed_products += 1
        if has_exceeded_error_limit(self.failed_products, self.max_errors):
            raise CloseSpider(f"max_errors_exceeded_{self.failed_products}")
