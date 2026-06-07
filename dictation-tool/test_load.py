"""
Minimal test - just load the transcriber, nothing else.
Run this to verify that the model loading itself works on your machine,
without PyQt or the keyboard library in the picture.

Usage:
    python test_load.py
"""

from config import load_config
from transcriber import Transcriber


def main():
    config = load_config()
    print(f"Loading {config['model_size']} on device={config.get('device', 'auto')}")
    print("(may take a while on first run if model needs to be downloaded)")
    t = Transcriber(config["model_size"], config.get("device", "auto"))
    print(f"\n SUCCESS! Model loaded on {t.device}")
    print(" If you see this line, basic loading works fine.")


if __name__ == "__main__":
    main()
