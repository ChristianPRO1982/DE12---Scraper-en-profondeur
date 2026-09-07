import logging

import pytest
from scrapy.exceptions import NotConfigured

from books_catalog_scraper.pipelines import PostgresPipeline


class FakeSettings:
    def __init__(self, enabled: bool) -> None:
        self.enabled = enabled

    def getbool(self, name: str, default: bool = False) -> bool:
        assert name == "POSTGRES_ENABLED"
        return self.enabled if self.enabled is not None else default


class FakeCrawler:
    def __init__(self, enabled: bool) -> None:
        self.settings = FakeSettings(enabled)


class FakeConnection:
    def __init__(self) -> None:
        self.commits = 0
        self.rollbacks = 0
        self.closed = False

    def commit(self) -> None:
        self.commits += 1

    def rollback(self) -> None:
        self.rollbacks += 1

    def close(self) -> None:
        self.closed = True


def test_pipeline_is_disabled_by_default() -> None:
    with pytest.raises(NotConfigured, match="desactive"):
        PostgresPipeline.from_crawler(FakeCrawler(enabled=False))


def test_pipeline_is_enabled_by_setting() -> None:
    assert isinstance(PostgresPipeline.from_crawler(FakeCrawler(enabled=True)), PostgresPipeline)


def test_open_and_close_spider_manage_connection(monkeypatch, caplog) -> None:
    connection = FakeConnection()
    monkeypatch.setattr("books_catalog_scraper.pipelines.connect_postgres", lambda: connection)
    pipeline = PostgresPipeline()

    caplog.set_level(logging.INFO)
    pipeline.open_spider()
    pipeline.close_spider()

    assert pipeline.connection is connection
    assert connection.closed
    assert "Pipeline PostgreSQL active" in caplog.text
    assert "0 livres sauvegardes dans PostgreSQL" in caplog.text


def test_close_spider_ignores_missing_connection() -> None:
    pipeline = PostgresPipeline()

    pipeline.close_spider()

    assert pipeline.connection is None


def test_process_item_upserts_and_commits(monkeypatch) -> None:
    upserted_items = []
    connection = FakeConnection()

    def fake_upsert_book(received_connection, item):
        upserted_items.append((received_connection, item))

    monkeypatch.setattr("books_catalog_scraper.pipelines.upsert_book", fake_upsert_book)
    pipeline = PostgresPipeline()
    pipeline.connection = connection
    item = {"upc": "abc"}

    assert pipeline.process_item(item) == item

    assert upserted_items == [(connection, item)]
    assert connection.commits == 1
    assert connection.rollbacks == 0
    assert pipeline.books_saved == 1


def test_process_item_can_be_replayed_with_same_item(monkeypatch) -> None:
    upserted_items = []
    connection = FakeConnection()

    def fake_upsert_book(received_connection, item):
        upserted_items.append((received_connection, item))

    monkeypatch.setattr("books_catalog_scraper.pipelines.upsert_book", fake_upsert_book)
    pipeline = PostgresPipeline()
    pipeline.connection = connection
    item = {"upc": "abc"}

    pipeline.process_item(item)
    pipeline.process_item(item)

    assert upserted_items == [(connection, item), (connection, item)]
    assert connection.commits == 2
    assert connection.rollbacks == 0
    assert pipeline.books_saved == 2


def test_process_item_rolls_back_on_error(monkeypatch) -> None:
    connection = FakeConnection()

    def fake_upsert_book(received_connection, item):
        raise RuntimeError("db error")

    monkeypatch.setattr("books_catalog_scraper.pipelines.upsert_book", fake_upsert_book)
    pipeline = PostgresPipeline()
    pipeline.connection = connection

    with pytest.raises(RuntimeError, match="db error"):
        pipeline.process_item({"upc": "abc"})

    assert connection.commits == 0
    assert connection.rollbacks == 1
    assert pipeline.books_saved == 0


def test_process_item_rejects_missing_connection() -> None:
    pipeline = PostgresPipeline()

    with pytest.raises(RuntimeError, match="non initialisee"):
        pipeline.process_item({"upc": "abc"})
