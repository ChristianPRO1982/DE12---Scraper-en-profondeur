from decimal import Decimal

from scrapy import Request
from scrapy.exceptions import CloseSpider
from scrapy.http import HtmlResponse

from books_catalog_scraper.spiders.books_list import BooksListSpider


def make_response(html: str, url: str = "https://books.toscrape.com/") -> HtmlResponse:
    return HtmlResponse(
        url=url,
        body=html.encode(),
        encoding="utf-8",
    )


def test_parse_book_extracts_list_fields() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating Three"></p>
            <h3>
                <a href="catalogue/a-light-in-the-attic_1000/index.html"
                   title="A Light in the Attic">A Light in the ...</a>
            </h3>
            <p class="price_color">£51.77</p>
        </article>
        """
    )
    product = response.css("article.product_pod")[0]

    item = BooksListSpider().parse_book(product, response)

    assert item == {
        "title": "A Light in the Attic",
        "price_list": Decimal("51.77"),
        "rating": 3,
        "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    }


def test_parse_follows_next_link() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating One"></p>
            <h3><a href="catalogue/book_1/index.html" title="Book 1">Book 1</a></h3>
            <p class="price_color">£10.00</p>
        </article>
        <ul class="pager">
            <li class="next"><a href="catalogue/page-2.html">next</a></li>
        </ul>
        """
    )
    spider = BooksListSpider()

    results = list(spider.parse(response))

    assert results[0] == {
        "title": "Book 1",
        "price_list": Decimal("10.00"),
        "rating": 1,
        "product_url": "https://books.toscrape.com/catalogue/book_1/index.html",
    }
    assert isinstance(results[1], Request)
    assert results[1].url == "https://books.toscrape.com/catalogue/page-2.html"
    assert spider.pages_seen == 1


def test_parse_stops_without_next_link() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating Five"></p>
            <h3><a href="../book_2/index.html" title="Book 2">Book 2</a></h3>
            <p class="price_color">£20.00</p>
        </article>
        """,
        url="https://books.toscrape.com/catalogue/page-50.html",
    )
    spider = BooksListSpider()

    results = list(spider.parse(response))

    assert results == [
        {
            "title": "Book 2",
            "price_list": Decimal("20.00"),
            "rating": 5,
            "product_url": "https://books.toscrape.com/book_2/index.html",
        }
    ]
    assert spider.pages_seen == 1


def test_parse_book_rejects_missing_title() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating Three"></p>
            <h3><a href="catalogue/book_1/index.html">Book 1</a></h3>
            <p class="price_color">£10.00</p>
        </article>
        """
    )
    product = response.css("article.product_pod")[0]

    try:
        BooksListSpider().parse_book(product, response)
    except ValueError as error:
        assert "Titre absent" in str(error)
    else:
        raise AssertionError("ValueError attendu")


def test_parse_book_rejects_missing_product_url() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating Three"></p>
            <h3><a title="Book 1">Book 1</a></h3>
            <p class="price_color">£10.00</p>
        </article>
        """
    )
    product = response.css("article.product_pod")[0]

    try:
        BooksListSpider().parse_book(product, response)
    except ValueError as error:
        assert "URL produit absente" in str(error)
    else:
        raise AssertionError("ValueError attendu")


def test_parse_ignores_invalid_product_and_continues() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating Unknown"></p>
            <h3><a href="catalogue/bad/index.html" title="Bad Book">Bad Book</a></h3>
            <p class="price_color">£10.00</p>
        </article>
        <article class="product_pod">
            <p class="star-rating Two"></p>
            <h3><a href="catalogue/good/index.html" title="Good Book">Good Book</a></h3>
            <p class="price_color">£12.50</p>
        </article>
        """
    )
    spider = BooksListSpider()

    results = list(spider.parse(response))

    assert results == [
        {
            "title": "Good Book",
            "price_list": Decimal("12.50"),
            "rating": 2,
            "product_url": "https://books.toscrape.com/catalogue/good/index.html",
        }
    ]
    assert spider.books_seen == 1
    assert spider.failed_products == 1


def test_parse_stops_when_error_limit_is_exceeded() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating Unknown"></p>
            <h3><a href="catalogue/bad/index.html" title="Bad Book">Bad Book</a></h3>
            <p class="price_color">£10.00</p>
        </article>
        """
    )
    spider = BooksListSpider(max_errors=0)

    try:
        list(spider.parse(response))
    except CloseSpider as error:
        assert error.reason == "max_errors_exceeded_1"
    else:
        raise AssertionError("CloseSpider attendu")

    assert spider.failed_products == 1


def test_parse_ignores_duplicate_product_url() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating Two"></p>
            <h3><a href="catalogue/book/index.html" title="First">First</a></h3>
            <p class="price_color">£12.50</p>
        </article>
        <article class="product_pod">
            <p class="star-rating Four"></p>
            <h3><a href="catalogue/book/index.html" title="Duplicate">Duplicate</a></h3>
            <p class="price_color">£15.50</p>
        </article>
        """
    )
    spider = BooksListSpider()

    results = list(spider.parse(response))

    assert results == [
        {
            "title": "First",
            "price_list": Decimal("12.50"),
            "rating": 2,
            "product_url": "https://books.toscrape.com/catalogue/book/index.html",
        }
    ]
    assert spider.books_seen == 1
    assert spider.duplicate_product_urls == 1
