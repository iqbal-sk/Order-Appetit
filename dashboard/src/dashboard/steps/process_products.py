from typing_extensions import Annotated
from loguru import logger
from zenml import get_step_context, step
import pandas as pd

@step
def process_product_names(
        products: pd.DataFrame
) -> Annotated[pd.DataFrame, "processed_products"]:
    """Processes and standardizes product names"""
    logger.info("Processing product names")

    try:
        # Clean product names
        processed_df = products.copy()
        processed_df['name'] = processed_df['name'].str.strip()
        processed_df = processed_df.drop_duplicates(subset=['name'])

        step_context = get_step_context()
        metadata = {
            "processing": {
                "initial_count": int(len(products)),  # Convert to native Python int
                "processed_count": int(len(processed_df)),  # Convert to native Python int
                "duplicates_removed": int(len(products) - len(processed_df)),  # Convert to native Python int
                "sample_products": processed_df['name'].head(5).tolist()
            },
            "statistics": {
                "null_values": int(processed_df['name'].isnull().sum()),  # Convert to native Python int
                "empty_values": int((processed_df['name'] == '').sum())  # Convert to native Python int
            }
        }
        step_context.add_output_metadata(output_name="processed_products", metadata=metadata)

        return processed_df

    except Exception as e:
        logger.error(f"Product name processing failed: {str(e)}")
        raise