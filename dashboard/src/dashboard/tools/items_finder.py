import os

from crewai_tools import tool
import torch
from sentence_transformers import SentenceTransformer, util
from pinecone import Pinecone


@tool("Food Items Finder")
def filter_items(item_name: str) -> str:
    """
    Find food names semantically equivalent to the food name in user query

    Args:
        item_name (str): food name from user query.

    Returns:
        str: string containing food names semantically equivalent to provided item_name.
    """

    try:

        from dotenv import load_dotenv

        load_dotenv()
        pinecone_key = os.getenv('PINECONE_API_KEY')
        pc = Pinecone(api_key=pinecone_key)
        index_name = "food"
        index = pc.Index(index_name)


        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L12-v2').to(device)


        item_embedding =  model.encode(item_name, convert_to_tensor=True).cpu().numpy().tolist()


        query_response = index.query(
            vector=item_embedding,
            top_k=20,
            include_metadata=True
        )

        equivalent_items = []
        for match in query_response['matches']:
            equivalent_items.append(match['metadata']['food_item'])


        if not equivalent_items:
            return "No semantically equivalent food items found."

        # Convert list to string and remove duplicates
        return ", ".join(set(equivalent_items))

    except Exception as e:
        return f"Error in Food Items Finder: {str(e)}"

# Test code (commented out)
if __name__ == "__main__":
    from time import time

    start = time()
    test_item = "Mac and Cheese"
    food_items_finder = filter_items
    result = food_items_finder(test_item)
    print(f"Semantically equivalent food items to '{test_item}':")
    print(result)
    end = time()

    print(end - start)