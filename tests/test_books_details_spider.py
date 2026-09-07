from decimal import Decimal

from scrapy import Request
from scrapy.http import HtmlResponse

from books_catalog_scraper.spiders.books_details import (
    BooksDetailsSpider,
    required_field,
    required_text,
)


def make_response(
    html: str,
    url: str = "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
) -> HtmlResponse:
    return HtmlResponse(
        url=url,
        body=html.encode(),
        encoding="utf-8",
    )


def product_page_html(description: str = "<p>A useful description.</p>") -> str:
    return f"""
    <ul class="breadcrumb">
        <li><a href="../../index.html">Home</a></li>
        <li><a href="../category/books_1/index.html">Books</a></li>
        <li><a href="../category/books/poetry_23/index.html">Poetry</a></li>
        <li class="active">A Light in the Attic</li>
    </ul>
    <div id="product_gallery">
        <img src="../../media/cache/book.jpg" alt="A Light in the Attic" />
    </div>
    <div class="product_main">
        <h1>A Light in the Attic</h1>
        <p class="price_color">£51.77</p>
        <p class="instock availability">In stock (22 available)</p>
        <p class="star-rating Three"></p>
    </div>
    <div id="product_description"></div>
    {description}
    <table class="table table-striped">
        <tr><th>UPC</th><td>a897fe39b1053632</td></tr>
        <tr><th>Product Type</th><td>Books</td></tr>
        <tr><th>Price (excl. tax)</th><td>£51.77</td></tr>
        <tr><th>Price (incl. tax)</th><td>£51.77</td></tr>
        <tr><th>Tax</th><td>£0.00</td></tr>
        <tr><th>Availability</th><td>In stock (22 available)</td></tr>
        <tr><th>Number of reviews</th><td>0</td></tr>
    </table>
    """


def list_page_html() -> str:
    return """
    <article class="product_pod">
        <p class="star-rating Three"></p>
        <h3>
            <a href="catalogue/a-light-in-the-attic_1000/index.html"
               title="A Light in the Attic">A Light in the ...</a>
        </h3>
        <p class="price_color">£51.77</p>
    </article>
    <ul class="pager">
        <li class="next"><a href="catalogue/page-2.html">next</a></li>
    </ul>
    """


def list_book() -> dict:
    return {
        "title": "A Light in the Attic",
        "price_list": Decimal("51.77"),
        "rating": 3,
        "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
    }


def test_extract_product_details_reads_product_information_by_label() -> None:
    response = make_response(product_page_html())

    item = BooksDetailsSpider().extract_product_details(response, list_book())

    assert item == {
        "upc": "a897fe39b1053632",
        "title": "A Light in the Attic",
        "product_url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
        "category": "Poetry",
        "rating": 3,
        "price_list": Decimal("51.77"),
        "price_excl_tax": Decimal("51.77"),
        "price_incl_tax": Decimal("51.77"),
        "tax": Decimal("0.00"),
        "stock_quantity": 22,
        "availability_text": "In stock (22 available)",
        "review_count": 0,
        "description": "A useful description.",
        "image_url": "https://books.toscrape.com/media/cache/book.jpg",
    }


def test_extract_product_information_ignores_rows_without_label() -> None:
    response = make_response(
        """
        <table class="table table-striped">
            <tr><td>Ignored value</td></tr>
            <tr><th>UPC</th><td>a897fe39b1053632</td></tr>
        </table>
        """
    )

    assert BooksDetailsSpider().extract_product_information(response) == {"UPC": "a897fe39b1053632"}


def test_extract_description_returns_none_when_missing() -> None:
    response = make_response(product_page_html(description=""))

    assert BooksDetailsSpider().extract_description(response) is None


def test_extract_category_rejects_missing_category() -> None:
    response = make_response(
        """
        <ul class="breadcrumb">
            <li><a href="../../index.html">Home</a></li>
            <li><a href="../category/books_1/index.html">Books</a></li>
        </ul>
        """
    )

    try:
        BooksDetailsSpider().extract_category(response)
    except ValueError as error:
        assert "Categorie introuvable" in str(error)
    else:
        raise AssertionError("ValueError attendu")


def test_required_field_rejects_missing_value() -> None:
    try:
        required_field({}, "UPC", "https://example.test/book")
    except ValueError as error:
        assert "Champ obligatoire absent 'UPC'" in str(error)
    else:
        raise AssertionError("ValueError attendu")


def test_required_text_rejects_missing_value() -> None:
    try:
        required_text(" ", "titre", "https://example.test/book")
    except ValueError as error:
        assert "Champ obligatoire absent 'titre'" in str(error)
    else:
        raise AssertionError("ValueError attendu")


def test_parse_list_page_schedules_product_and_next_requests() -> None:
    response = make_response(list_page_html(), url="https://books.toscrape.com/")
    spider = BooksDetailsSpider()

    results = list(spider.parse(response))

    assert len(results) == 2
    assert all(isinstance(result, Request) for result in results)
    assert (
        results[0].url
        == "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    )
    assert results[1].url == "https://books.toscrape.com/catalogue/page-2.html"
    assert spider.pages_seen == 1
    assert spider.product_requests == 1


def test_parse_list_page_ignores_duplicate_product_url() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating Three"></p>
            <h3><a href="catalogue/book/index.html" title="Book">Book</a></h3>
            <p class="price_color">£10.00</p>
        </article>
        <article class="product_pod">
            <p class="star-rating Four"></p>
            <h3><a href="catalogue/book/index.html" title="Book duplicate">Book</a></h3>
            <p class="price_color">£12.00</p>
        </article>
        """,
        url="https://books.toscrape.com/",
    )
    spider = BooksDetailsSpider()

    results = list(spider.parse(response))

    assert len(results) == 1
    assert spider.product_requests == 1
    assert spider.duplicate_product_urls == 1


def test_parse_list_page_ignores_invalid_product_card() -> None:
    response = make_response(
        """
        <article class="product_pod">
            <p class="star-rating Unknown"></p>
            <h3><a href="catalogue/book/index.html" title="Book">Book</a></h3>
            <p class="price_color">£10.00</p>
        </article>
        """,
        url="https://books.toscrape.com/",
    )
    spider = BooksDetailsSpider()

    assert list(spider.parse(response)) == []
    assert spider.failed_products == 1


def test_parse_product_yields_full_item() -> None:
    response = make_response(product_page_html())
    spider = BooksDetailsSpider()

    results = list(spider.parse_product(response, list_book()))

    assert len(results) == 1
    assert results[0]["upc"] == "a897fe39b1053632"
    assert spider.books_exported == 1


def test_parse_product_ignores_invalid_product_page() -> None:
    response = make_response("<html></html>")
    spider = BooksDetailsSpider()

    assert list(spider.parse_product(response, list_book())) == []
    assert spider.failed_products == 1


def test_closed_logs_summary() -> None:
    spider = BooksDetailsSpider()
    spider.books_exported = 2
    spider.failed_products = 1

    spider.closed("finished")
