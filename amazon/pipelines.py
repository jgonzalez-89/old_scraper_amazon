# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import datetime

class TransformDataPipeline:
    def process_item(self, item, spider):
        fecha_original = datetime.datetime.strptime(item["fecha"], "%d-%m-%Y")
        fecha_transformada = fecha_original.strftime("%Y-%m-%d")

        transformed_product = {
            "fecha": fecha_transformada,
            "nombre": item["nombre"],
            "ASIN": item["ASIN"],
            "historicos": {},
        }

        for vendedor, precio in zip(item["vendedores"], item["precios"]):
            if vendedor not in transformed_product["historicos"]:
                transformed_product["historicos"][vendedor] = []

            transformed_product["historicos"][vendedor].append(
                {
                    "fecha": fecha_transformada,
                    "precio": precio,
                }
            )

        return transformed_product