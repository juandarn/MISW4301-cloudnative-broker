import yaml
import os

def load_config(env="dev"):
    # Get the directory where this file is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(current_dir, "settings", f"{env}.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)
