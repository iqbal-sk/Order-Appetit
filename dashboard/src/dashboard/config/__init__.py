import yaml
from google.cloud.bigquery.magics import context
from qdrant_client.http import model


def load_configs():
    """Load agent and task configurations from YAML files"""
    config_path = 'config'

    # Load agents config
    with open('config/agents.yaml', 'r') as f:
        agents_config = yaml.safe_load(f)

    # Load tasks config
    with open('config/tasks.yaml', 'r') as f:
        tasks_config = yaml.safe_load(f)

    return agents_config, tasks_config

agents_config, tasks_config = load_configs()