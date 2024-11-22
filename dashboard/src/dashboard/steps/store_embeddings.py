from loguru import logger
from pinecone.grpc import PineconeGRPC as Pinecone
from pinecone import ServerlessSpec
from typing import Tuple, Annotated, Dict
from zenml import step, get_step_context
import pandas as pd
import numpy as np
import time

@step
def store_embeddings_pinecone(
        data: Tuple[pd.DataFrame, np.ndarray],
        pinecone_api_key: str,
        index_name: str,
        batch_size: int = 100
) -> Annotated[Dict, "storage_stats"]:
    """Stores product embeddings in Pinecone with batch processing"""
    logger.info("Storing embeddings in Pinecone")

    try:
        products, embeddings = data
        dimension = embeddings.shape[1]

        # Initialize Pinecone
        pc = Pinecone(api_key=pinecone_api_key)
        pc.delete_index(index_name)

        # Create index if it doesn't exist
        if not pc.has_index(index_name):
            logger.info(f"Creating new index: {index_name}")
            pc.create_index(
                name=index_name,
                dimension=dimension,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            # Wait for index to be ready
            while not pc.describe_index(index_name).status['ready']:
                time.sleep(1)

        # Get index
        index = pc.Index(index_name)

        total_vectors = len(products)
        vectors_uploaded = 0

        # Process in batches
        for i in range(0, total_vectors, batch_size):
            batch_end = min(i + batch_size, total_vectors)
            batch_products = products.iloc[i:batch_end]
            batch_embeddings = embeddings[i:batch_end]

            # Prepare vectors for upsert
            vectors = [
                {
                    'id': str(row['_id']),
                    'values': embedding.tolist(),
                    'metadata': {
                        'product_name': row['name'],
                        'original_id': str(row['_id'])
                    }
                }
                for embedding, (_, row) in zip(batch_embeddings, batch_products.iterrows())
            ]

            # Upsert batch
            logger.info(f"Upserting batch {i // batch_size + 1} of {(total_vectors + batch_size - 1) // batch_size}")
            index.upsert(vectors=vectors)

            vectors_uploaded += len(vectors)
            logger.info(f"Uploaded {vectors_uploaded}/{total_vectors} vectors")

            # Rate limiting pause
            time.sleep(0.5)

        # Get index statistics
        stats = index.describe_index_stats()

        print(stats)

        storage_stats = {
            "storage": {
                "total_vectors": stats.total_vector_count,
                "index_name": index_name,
                "dimension": dimension,
                "index_fullness": stats.total_vector_count / stats.dimension
            }
        }

        step_context = get_step_context()
        step_context.add_output_metadata(
            output_name="storage_stats",
            metadata=storage_stats
        )

        return storage_stats

    except Exception as e:
        logger.error(f"Pinecone storage failed: {str(e)}")
        raise
    finally:
        pass