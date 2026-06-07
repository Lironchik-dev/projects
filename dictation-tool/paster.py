import time
import pyperclip
import keyboard


def paste_text(text):
    if not text:
        return

    try:
        previous = pyperclip.paste()
    except Exception:
        previous = ""

    try:
        pyperclip.copy(text)
        time.sleep(0.05)
        keyboard.send("ctrl+v")
        time.sleep(0.3)
    finally:
        try:
            pyperclip.copy(previous)
        except Exception:
            pass
