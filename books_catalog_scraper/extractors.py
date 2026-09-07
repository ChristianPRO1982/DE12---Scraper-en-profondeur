import scrapy
from scrapy import Selector

from books_catalog_scraper.parsers import clean_text, parse_price, parse_rating


def extract_list_book(product: Selector, response: scrapy.http.Response) -> dict:
    title = clean_text(product.css("h3 a::attr(title)").get())
    product_path = product.css("h3 a::attr(href)").get()
    price_text = product.css("p.price_color::text").get()
    rating_class = product.css("p.star-rating::attr(class)").get()

    if not title:
        raise ValueError(f"Titre absent sur la page {response.url}")
    if not product_path:
        raise ValueError(f"URL produit absente pour {title!r}")

    return {
        "title": title,
        "price_list": parse_price(price_text),
        "rating": parse_rating(rating_class),
        "product_url": response.urljoin(product_path),
    }
