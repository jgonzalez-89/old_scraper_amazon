import os
import sys
import subprocess
import datetime
import requests
import logging
import shutil

logging.basicConfig(
    filename="launcher.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def run_scraper(scraper_name, json_file_path, json_file_name):

    # Elimina el archivo si existe antes de empezar el scraper
    if os.path.isfile(json_file_path):
        os.remove(json_file_path)

    project_path = os.path.dirname(os.path.abspath(__file__))
    scraper_path = os.path.join(project_path, scraper_name)
    os.chdir(scraper_path)
    sys.path.append(scraper_path)
    try:
        cmd = f"scrapy crawl {scraper_name} -o {json_file_name}"
        subprocess.run(cmd, shell=True, check=True)
        logging.info(f"Scraper {scraper_name} ejecutado exitosamente")
    except Exception as e:
        logging.error(f"Error al ejecutar el scraper {scraper_name}: {e}")
        raise
    finally:
        os.chdir(project_path)
        return scraper_path


def send_file_to_api(file_path, api_url):
    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = requests.post(api_url, files=files)
            response.raise_for_status()
            logging.info(f"Archivo {file_path} enviado a la API exitosamente")
        return response
    except Exception as e:
        logging.error(f"Error al enviar el archivo {file_path} a la API: {e}")
        raise


def main():
    try:
        date_string = datetime.datetime.now().strftime("%Y-%m-%d")
        json_file_name = f"{date_string}.json"

        # Scraper de Amazon
        scraper_path = os.path.dirname(os.path.abspath(__file__))
        json_file_path = os.path.join(scraper_path, f"amazon", json_file_name)
        run_scraper("amazon", json_file_path, json_file_name)

        api_url_amazon = "https://yixiephe4z.eu-west-1.awsapprunner.com/amazon/file/"
        send_file_to_api(json_file_path, api_url_amazon)
        shutil.move(json_file_path, f"./amazon_logs/{json_file_name}")

    except Exception as e:
        logging.error(f"Error en el proceso principal: {e}")


if __name__ == "__main__":
    main()