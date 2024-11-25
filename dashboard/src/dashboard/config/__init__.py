import yaml


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

def load_schema_config():

    with open('config/schema.yaml', 'r') as f:
        schema_config = yaml.safe_load(f)

    return schema_config

agents_config, tasks_config = load_configs()
schema_config = load_schema_config()