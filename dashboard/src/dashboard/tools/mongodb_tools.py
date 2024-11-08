from crewai_tools import tool
from pymongo.mongo_client import MongoClient
from collections import defaultdict
import json
from typing import Dict, Union

@tool("MongoDB Schema Analyzer")
def analyze_mongodb_schema(collection_name: str, database_name: str, mongodb_uri: str, sample_size: int = 50) -> str:
    """
    Analyzes the schema of a MongoDB collection and returns the field types and structure.

    Args:
        collection_name (str): Name of the MongoDB collection to analyze
        database_name (str): Name of the MongoDB database
        mongodb_uri (str): MongoDB connection URI
        sample_size (int): Number of documents to sample for schema analysis

    Returns:
        str: JSON string containing the collection schema with field names and their types
    """
    try:
        # Connect to MongoDB
        client = MongoClient(mongodb_uri)
        db = client[database_name]
        collection = db[collection_name]

        # Initialize schema dictionary
        schema = defaultdict(set)

        def analyze_nested_schema(document: Dict, parent_key: str = "") -> None:
            """Recursively analyze nested documents and arrays"""
            for key, value in document.items():
                current_key = f"{parent_key}.{key}" if parent_key else key

                if isinstance(value, dict):
                    schema[current_key].add("dict")
                    analyze_nested_schema(value, current_key)
                elif isinstance(value, list):
                    schema[current_key].add("list")
                    if value:  # If list is not empty, analyze its first element
                        if isinstance(value[0], dict):
                            analyze_nested_schema(value[0], f"{current_key}[]")
                        else:
                            schema[f"{current_key}[]"].add(type(value[0]).__name__)
                else:
                    schema[current_key].add(type(value).__name__)

        # Get sample documents
        sample_documents = collection.aggregate([
            {"$sample": {"size": sample_size}}
        ])

        # Analyze each document
        for doc in sample_documents:
            analyze_nested_schema(doc)

        # Convert sets to lists for JSON serialization
        formatted_schema = {
            "collection_name": collection_name,
            "database_name": database_name,
            "sample_size": sample_size,
            "fields": {k: list(v) for k, v in schema.items()}
        }

        # # Add field statistics
        # field_stats = {}
        # for field in schema.keys():
        #     count = collection.count_documents({field: {"$exists": True}})
        #     percentage = (count / collection.count_documents({})) * 100
        #     field_stats[field] = {
        #         "count": count,
        #         "percentage": round(percentage, 2)
        #     }

        # formatted_schema["field_stats"] = field_stats

        return json.dumps(formatted_schema)

    except Exception as e:
        return f"Error analyzing MongoDB schema: {str(e)}"
    finally:
        client.close()