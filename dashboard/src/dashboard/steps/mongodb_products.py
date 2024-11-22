from typing_extensions import Annotated
from loguru import logger
from zenml import get_step_context, step
from pymongo import MongoClient
import pandas as pd

@step
def fetch_mongodb_products(
        mongodb_uri: str,
        database_name: str
) -> Annotated[pd.DataFrame, "raw_products"]:
    """Establishes MongoDB connection and fetches product data"""
    logger.info(f"Establishing MongoDB connection")

    try:
        # Establish connection
        client = MongoClient(mongodb_uri)
        client.admin.command('ping')

        # Log connection success
        step_context = get_step_context()
        step_context.add_output_metadata(
            output_name="raw_products",
            metadata={
                "connection": {
                    "status": "successful",
                    "uri": mongodb_uri.split('@')[-1]
                }
            }
        )

        # Fetch data
        logger.info(f"Fetching products from database: {database_name}")
        db = client[database_name]
        products = list(db.products.find({}, {"_id": 1, "name": 1}))
        df = pd.DataFrame(products)

        # Add extraction metadata
        metadata = {
            "extraction": {
                "total_products": len(products),
                "unique_products": df['name'].nunique(),
                "database": database_name,
                "collection": "products",
                "fields_extracted": ["_id", "name"]
            }
        }
        step_context.add_output_metadata(output_name="raw_products", metadata=metadata)

        return df

    except Exception as e:
        logger.error(f"MongoDB operation failed: {str(e)}")
        raise
    finally:
        if 'client' in locals():
            client.close()