import scrapy
import re
import random
import time
import requests
from scrapy.spiders import Spider
from scrapy import Request
import datetime
from scrapy_selenium import SeleniumRequest
from user_agent import generate_user_agent
import logging


logging.getLogger("protego").setLevel(logging.WARNING)
logging.getLogger("selenium.webdriver.remote.remote_connection").setLevel(
    logging.WARNING
)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)


class AmazonSpider(scrapy.Spider):
    name = "amazon"

    def __init__(self, asin=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if asin:
            self.asin = asin.split(",")
        else:
            self.asin = [
                "B005FNKMF0",
                "B006TH5DUK",
                # "B0073FD66A",
                # "B0073FO9AM",
                # "B0073FTCJU",
                # "B007XNNF72",
                # "B00GB8IA5C",
                # "B00GB8V338",
                # "B00GCCQ3DI",
                # "B00GHUZDFO",
                # "B00GTW4QQ2",
                # "B00GTW4S3S",
                # "B00HUEGDZU",
                # "B00OKME7S0",
                # "B00OOUSJ0A",
                # "B00QFKIYX4",
                # "B00U1JHWR4",
                # "B00VO6BRGK",
                # "B00ZPQ129C",
                # "B011DCMQZA",
                # "B0165H0JHU",
                # "B06XSF4R1X",
                # "B06ZZ6CDY1",
                # "B073WW3KZL",
                # "B074HB44JQ",
                # "B075PLPVWF",
                # "B07661NQDH",
                # "B07BNRR82Z",
                # "B07RRBZF7T",
                # "B07ZJ82DFL",
                # "B07ZL56NS7",
                # "B07ZL6B5SS",
                # "B0813DB98Y",
                # "B08SXQTV52",
                # "B08SXSWC7Y",
                # "B015UCTS5U",
                # "B015UD5JLG",
                # "B015UDH09A",
                # "B0190MZQ34",
                # "B01DRZEK96",
                # "B01JTHDLTQ",
                # "B01MUI8JBV",
                # "B01N36O3RT",
                # "B01N5S2BHO",
                # "B01N7UYUVY",
                # "B01N9UH4T9",
                # "B01NAVYVLG",
                # "B01NB0TI00",
                # "B01NBXIKIL",
                # "B01ND3RNF9",
                # "B06XD65SNZ",
                # "B06XDGDTM9",
                # "B06Y3NHWVG",
                # "B075WD97B2",
                # "B077NF3R4W",
                # "B077NGWYRX",
                # "B07BZDZ3JM",
                # "B07BZM3HQH",
                # "B07C7KCF4W",
                # "B07KJB395Z",
                # "B07KJBL9RK",
                # "B07KJD3N8M",
                # "B07KK15DY1",
                # "B07L5Q9F49",
                # "B07Z1BWSYX",
                # "B085GK4LQF",
            ]

    def start_requests(self):
        for asin in self.asin:
            url = f"https://www.amazon.es/gp/offer-listing/{asin}"
            print(f"URL: {url}")  # Agrega esta línea para depurar
            headers = {"User-Agent": generate_user_agent()}

            print(f"Headers: {headers}")

            yield SeleniumRequest(
                url=url,
                callback=self.parse,
                headers=headers,
                meta={
                    "handle_httpstatus_list": [503],
                    "dont_redirect": True,
                    "original_url": url,
                },
            )

    def parse(self, response):
        try:
            codigo_ASIN = self.extract_codigo(response.url)
            fecha = datetime.datetime.now().strftime("%d-%m-%Y")
            nombre = self.extract_nombre(response)

            offers = response.xpath(
                "//*[@id='aod-pinned-offer']|//*[@id='aod-offer']")
            vendedores = []
            precios = []

            for offer in offers:
                price = offer.xpath(
                    ".//span[contains(@class, 'a-price')]/span[contains(@class, 'a-offscreen')]/text()"
                ).get()
                vendor = offer.xpath(
                    ".//*[@id='aod-offer-soldBy']/div/div/div[2]/a/text()"
                ).get()

                if price:
                    price = float(price.replace("€", "").replace(",", "."))
                    precios.append(price)

                if vendor:
                    vendedores.append(vendor.strip())

            if not vendedores or not precios:
                raise Exception("No se encontraron vendedores o precios")
            else:
                yield {
                    "fecha": fecha,
                    "nombre": nombre,
                    "vendedores": vendedores,
                    "precios": precios,
                    "ASIN": codigo_ASIN,
                }
                time.sleep(random.uniform(1, 3))

        except Exception as e:
            retry_times = response.meta.get("retry_times", 0) + 1

            if retry_times <= 5:  # Puedes ajustar el número máximo de intentos
                self.logger.info(
                    f"Reintentando {response.meta['original_url']} (intento {retry_times}) - Error: {str(e)}"
                )
                time.sleep(
                    random.uniform(1, 3)
                )  # Agrega tiempo de espera entre intentos
                # Agrega encabezados
                headers = {"User-Agent": generate_user_agent()}
                yield SeleniumRequest(
                    url=response.meta["original_url"],
                    callback=self.parse,
                    headers=headers,
                    meta={
                        "handle_httpstatus_list": [503],
                        "dont_redirect": True,
                        "retry_times": retry_times,
                        "original_url": response.meta["original_url"],
                    },
                    dont_filter=True,  # Agrega esta línea
                )
                return

    @staticmethod
    def extract_precio(response):
        precio_str = response.xpath(
            ".//span[contains(@class, 'a-price-whole')]/text()"
        ).get()
        if precio_str is not None:
            precio_str = precio_str.strip()
            return float(precio_str.replace(",", "."))
        return None

    @staticmethod
    def extract_nombre(response):
        nombre = response.xpath("//*[@id='productTitle']/text()").get()
        if nombre:
            return nombre.replace('"', "").lower().strip()
        return None

    @staticmethod
    def extract_codigo(url):
        codigo_regex = r"\b[B0-9][A-Z0-9]{9}\b"
        match = re.search(codigo_regex, url)
        if match:
            return match.group(0)
        return None
