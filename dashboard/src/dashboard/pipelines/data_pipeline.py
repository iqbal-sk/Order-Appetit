from zenml import pipeline
from zenml.client import Client
from src.steps.mongodb_products import fetch_mongodb_products
from src.steps.process_products import process_product_names
from src.steps.product_statistics import generate_product_statistics

@pipeline
def product_data_pipeline(
        mongodb_uri: str,
        database_name: str
) -> str:
    """Pipeline to process and analyze product data"""


    # Fetch raw product data
    raw_products = fetch_mongodb_products(mongodb_uri, database_name)

    # Process product names
    processed_products = process_product_names(raw_products)

    return processed_products


if __name__ == '__main__':
    import urllib.parse

    client = Client()
    username = urllib.parse.quote_plus("UB_6872023")
    password = urllib.parse.quote_plus("UB_2024!")

    uri = f"mongodb://{username}:{password}@atlas-sql-643e3030d126783c73656b9e-qrodv.a.query.mongodb.net/?ssl=true&authSource=admin&appName=atlas-sql-643e3030d126783c73656b9e"

    database_name = 'appetit_db'

    product_data_pipeline(uri, database_name)
