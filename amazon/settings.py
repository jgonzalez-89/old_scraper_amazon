BOT_NAME = "amazon"

SPIDER_MODULES = ["amazon.spiders"]
NEWSPIDER_MODULE = "amazon.spiders"


LOG_LEVEL = 'DEBUG'
# CRITICAL
# ERROR
# WARNING (default)
# INFO
# DEBUG

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

ITEM_PIPELINES = {
    'amazon.pipelines.TransformDataPipeline': 300,
}

DOWNLOADER_MIDDLEWARES = {
    'amazon.middlewares.SeleniumMiddleware': 800,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

SELENIUM_DRIVER_NAME = "firefox"

SELENIUM_DRIVER_ARGUMENTS = ["-headless"]
