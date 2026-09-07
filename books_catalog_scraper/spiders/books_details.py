from collections.abc import Iterator

import scrapy
from scrapy import Request

from books_catalog_scraper.extractors import extract_list_book
from books_catalog_scraper.parsers import (
    clean_text,
    parse_int,
    parse_price,
    parse_rating,
    parse_stock,
)


class BooksDetailsSpider(scrapy.Spider):
    name = "books_details"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def __init__(self, limit: str | int | None = None, *args: object, **kwargs: object) -> None:
        super().__init__(*args, **kwargs)
        self.limit = parse_limit(limit)
        self.pages_seen = 0
        self.product_urls_seen: set[str] = set()
        self.product_requests = 0
        self.books_exported = 0
        self.failed_products = 0
        self.duplicate_product_urls = 0

    def parse(self, response: scrapy.http.Response) -> Iterator[Request]:
        self.pages_seen += 1

        products = response.css("article.product_pod")
        self.logger.info(
            "Page de liste parcourue: %s (%s livres trouves)",
            response.url,
            len(products),
        )

        for product in products:
            if self.has_reached_limit():
                break

            try:
                list_book = extract_list_book(product, response)
            except ValueError as error:
                self.failed_products += 1
                self.logger.warning("Livre ignore sur %s: %s", response.url, error)
                continue

            product_url = list_book["product_url"]
            if product_url in self.product_urls_seen:
                self.duplicate_product_urls += 1
                self.logger.warning("URL produit dupliquee ignoree: %s", product_url)
                continue

            self.product_urls_seen.add(product_url)
            self.product_requests += 1
            yield response.follow(
                product_url,
                callback=self.parse_product,
                cb_kwargs={"list_book": list_book},
            )

        next_url = response.css("li.next a::attr(href)").get()
        if next_url and not self.has_reached_limit():
            yield response.follow(next_url, callback=self.parse)
        else:
            self.logger.info(
                (
                    "Collecte des listes terminee: %s pages parcourues, "
                    "%s fiches programmees, %s cartes ignorees, %s doublons URL ignores"
                ),
                self.pages_seen,
                self.product_requests,
                self.failed_products,
                self.duplicate_product_urls,
            )

    def parse_product(self, response: scrapy.http.Response, list_book: dict) -> Iterator[dict]:
        try:
            product = self.extract_product_details(response, list_book)
        except ValueError as error:
            self.failed_products += 1
            self.logger.warning("Fiche produit ignoree %s: %s", response.url, error)
            return

        self.books_exported += 1
        yield product

    def extract_product_details(self, response: scrapy.http.Response, list_book: dict) -> dict:
        product_information = self.extract_product_information(response)
        availability_text = required_field(product_information, "Availability", response.url)
        image_path = response.css("#product_gallery img::attr(src)").get()

        return {
            "upc": required_field(product_information, "UPC", response.url),
            "title": required_text(
                response.css("div.product_main h1::text").get(), "titre", response.url
            ),
            "product_url": response.url,
            "category": self.extract_category(response),
            "rating": parse_rating(
                response.css("div.product_main p.star-rating::attr(class)").get()
            ),
            "price_list": list_book["price_list"],
            "price_excl_tax": parse_price(
                required_field(product_information, "Price (excl. tax)", response.url)
            ),
            "price_incl_tax": parse_price(
                required_field(product_information, "Price (incl. tax)", response.url)
            ),
            "tax": parse_price(required_field(product_information, "Tax", response.url)),
            "stock_quantity": parse_stock(availability_text),
            "availability_text": availability_text,
            "review_count": parse_int(
                required_field(product_information, "Number of reviews", response.url)
            ),
            "description": self.extract_description(response),
            "image_url": response.urljoin(image_path) if image_path else None,
        }

    def extract_product_information(self, response: scrapy.http.Response) -> dict[str, str]:
        product_information = {}

        for row in response.css("table.table.table-striped tr"):
            label = clean_text(row.css("th::text").get())
            value = clean_text(row.css("td::text").get())
            if label:
                product_information[label] = value

        return product_information

    def extract_category(self, response: scrapy.http.Response) -> str:
        categories = [
            text
            for text in (
                clean_text(value) for value in response.css("ul.breadcrumb li a::text").getall()
            )
            if text and text not in {"Home", "Books"}
        ]

        if not categories:
            raise ValueError(f"Categorie introuvable sur {response.url}")

        return categories[-1]

    def extract_description(self, response: scrapy.http.Response) -> str | None:
        description = clean_text(response.css("#product_description + p::text").get())
        return description or None

    def closed(self, reason: str) -> None:
        self.logger.info(
            ("Collecte des fiches terminee: %s livres exportes, %s echecs, raison=%s"),
            self.books_exported,
            self.failed_products,
            reason,
        )

    def has_reached_limit(self) -> bool:
        return self.limit is not None and self.product_requests >= self.limit


def required_field(product_information: dict[str, str], field_name: str, product_url: str) -> str:
    value = clean_text(product_information.get(field_name))
    if not value:
        raise ValueError(f"Champ obligatoire absent {field_name!r} sur {product_url}")

    return value


def required_text(value: str | None, field_name: str, product_url: str) -> str:
    cleaned_value = clean_text(value)
    if not cleaned_value:
        raise ValueError(f"Champ obligatoire absent {field_name!r} sur {product_url}")

    return cleaned_value


def parse_limit(value: str | int | None) -> int | None:
    if value in {None, ""}:
        return None

    limit = int(value)
    if limit < 1:
        raise ValueError("Le parametre limit doit etre un entier positif")

    return limit
