import json
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "settings.json"

DEFAULT_CONFIG = {
    "hotkey": "ctrl+shift+space",
    "language": "he",
    "model_size": "large-v3",
    "device": "auto",
    "recording_mode": "toggle",
    "custom_dictionary": {
        "קלוד": "Claude",
        "פייתון": "Python",
        "ג'יפיטי": "GPT",
        "ג'י פי טי": "GPT"
    },
    "filler_words": {
        "he": ["אה", "אמ", "אממ", "כאילו", "יעני"],
        "en": ["um", "uh", "uhh", "umm", "like"],
        "ru": ["ну", "это", "как"]
    },
    "remove_filler_words": True,
    "use_custom_dictionary": True,
    "feedback": {
        "sound": True,
        "tray_icon_color": True,
        "screen_indicator": False,
        "overlay_window": False
    }
}


def load_config():
    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                config = json.load(f)
            for key, value in DEFAULT_CONFIG.items():
                if key not in config:
                    config[key] = value
            return config
        except (json.JSONDecodeError, OSError):
            pass
    save_config(DEFAULT_CONFIG)
    return DEFAULT_CONFIG.copy()


def save_config(config):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)
