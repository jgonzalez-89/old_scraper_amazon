from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver import Firefox

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException


from scrapy.utils.project import get_project_settings
from scrapy.http import HtmlResponse
from amazoncaptcha import AmazonCaptcha
import datetime
import requests
import tempfile
import time
import os


class SeleniumMiddleware:
    def __init__(self):
        # Obtiene las configuraciones del proyecto
        settings = get_project_settings()

        # Configura las opciones del navegador para Firefox
        options = FirefoxOptions()  # Esto se ha cambiado
        for argument in settings.get("SELENIUM_DRIVER_ARGUMENTS", []):
            options.add_argument(argument)

        # Configura el servicio y el navegador para Firefox
        service = FirefoxService(
            executable_path=GeckoDriverManager().install())
        self.driver = Firefox(service=service, options=options)

    def process_request(self, request, spider):
        self.driver.get(request.url)
        time.sleep(2)  # Pausa para asegurar que la página ha cargado
        
        # # Opcional: Guardar el contenido de la página en un archivo
        # #page_content = self.driver.page_source
        # #with open(f"debug_page{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}.html", "w", encoding="utf-8") as file:
        #     #file.write(page_content)
            
            
                # Verificar si se ha cargado la página de error
        try:
            error_message = self.driver.find_element(By.XPATH, "//b[contains(text(), 'Lo sentimos.')]")
            if error_message:
                spider.logger.info("Detectada página de error, intentando redirigir")
                try:
                    redirect_link = self.driver.find_element(By.XPATH, "//a[contains(@href, 'ref=cs_503_link')]")
                    redirect_link.click()  # Hacer clic en el enlace para redirigir
                    time.sleep(2)  # Esperar a que se cargue la nueva página
                except NoSuchElementException:
                    spider.logger.error("No se encontró el enlace de redirección en la página de error")
                    return HtmlResponse(url=request.url, status=504, body=b'', request=request)

        except NoSuchElementException:
            spider.logger.info("No se detectó la página de error")

        
        try:
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.ID, "all-offers-display"))
            )
        except TimeoutException:
            spider.logger.error("Tiempo de espera excedido para cargar el elemento")
            return HtmlResponse(url=request.url, status=504, body=b'', request=request)

        while self.detect_captcha():
            # Intenta resolver el CAPTCHA
            if not self.resolve_captcha():
                spider.logger.error(
                    'CAPTCHA no pudo ser resuelto. Abortando...')
                # Puedes decidir retornar una respuesta vacía o lanzar una excepción
                return HtmlResponse(url=request.url, status=503, body=b'', request=request)
            # Recarga la página después de resolver el CAPTCHA y verifica si hay más CAPTCHAs
            self.driver.get(request.url)
            time.sleep(2)

        # Retorna la respuesta normalmente si no hay CAPTCHA
        return HtmlResponse(self.driver.current_url, body=self.driver.page_source, encoding='utf-8', request=request)

    def detect_captcha(self):
        # Busca elementos de imagen que contengan 'captcha' en su URL.
        captcha_image_elements = self.driver.find_elements(By.XPATH, '//img[contains(@src,"captcha")]')
        # Si se encuentra al menos un elemento, entonces hay un CAPTCHA en la página.
        return len(captcha_image_elements) > 0

    def resolve_captcha(self):
        # Implementa la resolución de CAPTCHA utilizando la librería de AmazonCaptcha
        temp_file = None

        try:
            # Encuentra la URL de la imagen del CAPTCHA
            captcha_image_element = self.driver.find_elements(By.XPATH, '//img[contains(@src,"captcha")]')
            captcha_image_url = captcha_image_element[0].get_attribute('src') if captcha_image_element else None

            # Descarga la imagen del CAPTCHA y resuélvela
            response = requests.get(captcha_image_url, stream=True)
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            for block in response.iter_content(1024):
                if not block:
                    break
                temp_file.write(block)
            temp_file.close()

            # Resuelve el CAPTCHA
            solution = AmazonCaptcha(temp_file.name).solve()
            print("Solución CAPTCHA: ", solution)  # O usa logging

            # Rellena el texto del CAPTCHA resuelto y envía el formulario
            input_captcha = self.driver.find_element(By.ID, 'captchacharacters')
            input_captcha.send_keys(solution)
            submit_button = self.driver.find_element(By.XPATH, '//button[@type="submit"]')
            submit_button.click()
            # Espera para que el CAPTCHA se envíe y la página se recargue
            time.sleep(2)

            # Verifica si el CAPTCHA se resolvió correctamente
            if self.detect_captcha():
                return False  # CAPTCHA no se resolvió

            return True  # CAPTCHA resuelto
        except Exception as e:
            print(f"Error al resolver CAPTCHA: {e}")  # O usa logging
            return False
        finally:
            # Limpia y elimina el archivo temporal
            temp_file.close()
            os.unlink(temp_file.name)