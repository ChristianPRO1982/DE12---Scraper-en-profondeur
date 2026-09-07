from books_catalog_scraper import settings


def test_scrapy_project_settings_are_configured() -> None:
    assert settings.BOT_NAME == "books_catalog_scraper"
    assert settings.SPIDER_MODULES == ["books_catalog_scraper.spiders"]
    assert settings.NEWSPIDER_MODULE == "books_catalog_scraper.spiders"


def test_scrapy_crawler_behaves_politely() -> None:
    assert settings.ROBOTSTXT_OBEY is True
    assert settings.USER_AGENT.startswith("DE12-books-scraper/0.1")
    assert settings.DOWNLOAD_DELAY == 0.5
    assert settings.RANDOMIZE_DOWNLOAD_DELAY is True
    assert settings.CONCURRENT_REQUESTS_PER_DOMAIN == 2


def test_scrapy_logging_and_feeds_defaults() -> None:
    assert settings.LOG_LEVEL == "INFO"
    assert settings.FEEDS == {}
