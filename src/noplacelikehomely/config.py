import json
import os

CONFIG_PATH = os.path.expanduser("~/.noplacelikeconfig.json")
DEFAULT_CONFIG = {
    "upload_folder": "~/noplacelike/uploads",
    "download_folder": "~/Downloads"
}

def load_config():
    """Load config from CONFIG_PATH; create file with defaults if missing."""
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    except Exception:
        config = DEFAULT_CONFIG.copy()
    # Ensure default keys exist
    for key, value in DEFAULT_CONFIG.items():
        config.setdefault(key, value)
    return config

def save_config(config):
    """Save provided config into CONFIG_PATH."""
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=4)

def update_config(**kwargs):
    """Update config values and save."""
    config = load_config()
    config.update(kwargs)
    save_config(config)
    return config
