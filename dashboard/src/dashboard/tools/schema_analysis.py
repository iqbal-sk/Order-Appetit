from crewai_tools import tool
import json
from typing import Dict
from pathlib import Path
import yaml
from dashboard.src.dashboard.config import schema_config


@tool("MongoDB Schema Analyzer")
def analyze_local_schema(collection_name: str) -> str:
    """
    Analyzes schema of collection.

    Args:
        collection_name (str): Name of the collection to analyze


    Returns:
        str: JSON string containing the filtered schema with essential fields
    """
    try:
        config = schema_config

        schema_path = config.get("schema_paths", {}).get(collection_name)
        if not schema_path:
            return f"No schema path configured for collection: {collection_name}"

        # Load schema file
        with open(schema_path) as f:
            schema = json.load(f)


        return json.dumps(schema, indent=2)

    except Exception as e:
        return f"Error analyzing schema: {str(e)}"