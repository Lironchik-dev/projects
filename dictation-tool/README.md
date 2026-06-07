# Dictation Tool

A desktop application that turns speech into text in real time, using the
**Whisper** AI model (via `faster-whisper`). Press a global hotkey, speak, and the
transcribed text is cleaned up and pasted automatically wherever your cursor is.

## Features

- Audio recording with a global hotkey (toggle or push-to-talk)
- Speech-to-text using the Whisper AI model (GPU-accelerated when available)
- Removes filler words ("אה", "אמ", "um", "uh"...) in Hebrew, English and Russian
- Custom dictionary to fix common words (e.g. "פייתון" -> "Python")
- Automatic paste into the active window
- Clean dark-themed UI

## Architecture

The code is split into focused modules:

| File | Responsibility |
|------|----------------|
| `main.py` | Entry point and UI styling |
| `app.py` | Application logic / state machine |
| `gui.py` | The graphical interface |
| `audio_recorder.py` | Records microphone audio |
| `transcriber.py` | Runs the Whisper model |
| `text_processor.py` | Cleans up the transcribed text |
| `paster.py` | Pastes text into the active window |
| `config.py` | Loads / saves settings |

## Run it

```bash
pip install -r requirements.txt
python main.py
```

Settings (hotkey, language, model size, custom dictionary) live in `settings.json`.
