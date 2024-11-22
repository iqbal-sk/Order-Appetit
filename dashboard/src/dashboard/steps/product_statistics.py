from typing_extensions import Annotated
from loguru import logger
from zenml import get_step_context, step
import pandas as pd
from typing import Dict

@step
def generate_product_statistics(
        products: pd.DataFrame
) -> Annotated[Dict, "product_stats"]:
    """Generates statistics for processed products"""
    logger.info("Generating product statistics")

    try:
        stats = {
            "total_products": int(len(products)),  # Convert to native Python int
            "unique_products": int(products['name'].nunique()),  # Convert to native Python int
            "name_lengths": {
                "min": int(products['name'].str.len().min()),  # Convert to native Python int
                "max": int(products['name'].str.len().max()),  # Convert to native Python int
                "avg": float(products['name'].str.len().mean())  # Convert to native Python float
            }
        }

        step_context = get_step_context()
        step_context.add_output_metadata(output_name="product_stats", metadata=stats)

        return stats

    except Exception as e:
        logger.error(f"Statistics generation failed: {str(e)}")
        raise