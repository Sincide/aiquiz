import json
import os

CONFIG_FILE = 'quiz_config.json'
DEFAULT_CONFIG = {
    'data_dir': 'data',
    'ollama_model': 'llama2'
}


def load_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
    else:
        cfg = DEFAULT_CONFIG
        save_config(cfg)
    return cfg


def save_config(cfg: dict) -> None:
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(cfg, f, indent=2)
