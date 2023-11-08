BOT_NAME = "amazon"

SPIDER_MODULES = ["amazon.spiders"]
NEWSPIDER_MODULE = "amazon.spiders"


LOG_LEVEL = 'DEBUG'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

DOWNLOADER_MIDDLEWARES = {
    'amazon.middlewares.SeleniumMiddleware': 50,
}

ITEM_PIPELINES = {
    'amazon.pipelines.TransformDataPipeline': 800,
}


REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

SELENIUM_DRIVER_NAME = "firefox"


SELENIUM_DRIVER_ARGUMENTS = ["-headless"]
