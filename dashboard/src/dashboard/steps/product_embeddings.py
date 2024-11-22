from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from typing import List, Tuple
from typing_extensions import Annotated
from loguru import logger
import pandas as pd
from zenml import step, get_step_context
import numpy as np
import time

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def get_embeddings_batch(client: OpenAI, texts: List[str], model: str = "text-embedding-3-large") -> List[List[float]]:
    """Get embeddings for a batch of texts with retry logic"""
    try:
        response = client.embeddings.create(
            input=texts,
            model=model,
            encoding_format="float"
        )
        return [data.embedding for data in response.data]
    except Exception as e:
        logger.error(f"Error in batch embedding generation: {e}")
        raise


@step
def generate_product_embeddings(
        products: pd.DataFrame,
        openai_api_key: str,
        batch_size: int = 100,
        model: str = "text-embedding-3-large"
) -> Annotated[Tuple[pd.DataFrame, np.ndarray], "product_embeddings"]:
    """Generates embeddings for product names using OpenAI's API with batch processing"""
    logger.info(f"Generating embeddings using {model}")

    try:
        client = OpenAI(api_key=openai_api_key)
        product_names = products['name'].tolist()
        total_products = len(product_names)
        embeddings_list = []

        # Process in batches
        for i in range(0, total_products, batch_size):
            batch = product_names[i:min(i + batch_size, total_products)]
            logger.info(f"Processing batch {i // batch_size + 1} of {(total_products + batch_size - 1) // batch_size}")

            # Clean text
            batch = [text.replace("\n", " ").strip() for text in batch]

            # Get embeddings for batch
            batch_embeddings = get_embeddings_batch(client, batch, model)
            embeddings_list.extend(batch_embeddings)

            # Log progress
            processed = min(i + batch_size, total_products)
            logger.info(f"Processed {processed}/{total_products} products")

            # Rate limiting pause
            time.sleep(0.5)

        # Convert to numpy array
        embeddings = np.array(embeddings_list)

        # Log metadata about embeddings
        step_context = get_step_context()
        step_context.add_output_metadata(
            output_name="product_embeddings",
            metadata={
                "embedding_type": model,
                "embedding_dimensionality": embeddings.shape[1],
                "total_embeddings": len(embeddings),
                "batch_size": batch_size,
                "total_batches": (total_products + batch_size - 1) // batch_size,
                "sample_products": product_names[:5]
            }
        )

        return products, embeddings

    except Exception as e:
        logger.error(f"Embedding generation failed: {str(e)}")
        raise