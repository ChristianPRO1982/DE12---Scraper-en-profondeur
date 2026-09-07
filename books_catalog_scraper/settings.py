BOT_NAME = "books_catalog_scraper"

SPIDER_MODULES = ["books_catalog_scraper.spiders"]
NEWSPIDER_MODULE = "books_catalog_scraper.spiders"

ROBOTSTXT_OBEY = True
USER_AGENT = "DE12-books-scraper/0.1 (+https://github.com/student/de12-scraper-en-profondeur)"

DOWNLOAD_DELAY = 0.5
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS_PER_DOMAIN = 2

LOG_LEVEL = "INFO"
TELNETCONSOLE_ENABLED = False

FEEDS = {}
