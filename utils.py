import yaml
from pathlib import Path


def load_config():
    dir_path = Path(__file__).resolve().parent
    config_path = dir_path / "config.yml"
    with open(config_path, encoding="utf-8") as file:
        return yaml.safe_load(file)
