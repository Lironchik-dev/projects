import os
import threading

from PyQt5.QtCore import QObject, pyqtSignal, QCoreApplication

from config import save_config
from audio_recorder import AudioRecorder
from transcriber import Transcriber
from text_processor import TextProcessor
from paster import paste_text


STATE_LOADING = "loading"
STATE_IDLE = "idle"
STATE_RECORDING = "recording"
STATE_TRANSCRIBING = "transcribing"
STATE_ERROR = "error"


class DictationApp(QObject):
    state_changed = pyqtSignal(str)
    info_changed = pyqtSignal(str)
    transcription_done = pyqtSignal(str, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, config, transcriber):
        super().__init__()
        self.config = config
        self.transcriber = transcriber
        self.recorder = AudioRecorder()
        self.processor = TextProcessor(self.config)
        self.state = STATE_IDLE
        self._lock = threading.Lock()

    def emit_initial_state(self):
        device = getattr(self.transcriber, "device", "?")
        self.info_changed.emit(f"מוכן (פועל על {device.upper()})")
        self.state_changed.emit(self.state)

    def reload_transcriber(self):
        self._set_state(STATE_LOADING)
        self.info_changed.emit(f"טוען מודל {self.config['model_size']}... (החלון יקפא לרגע)")
        QCoreApplication.processEvents()

        try:
            self.transcriber = Transcriber(
                self.config["model_size"],
                self.config.get("device", "auto"),
            )
            device = self.transcriber.device
            self.info_changed.emit(f"מוכן (פועל על {device.upper()})")
            self._set_state(STATE_IDLE)
        except Exception as e:
            self._set_state(STATE_ERROR)
            self.error_occurred.emit(f"טעינת המודל נכשלה: {e}")

    def toggle_recording(self):
        with self._lock:
            if self.state == STATE_LOADING:
                self.info_changed.emit("עוד טוען את המודל, רגע...")
                return
            if self.state == STATE_TRANSCRIBING:
                self.info_changed.emit("עוד מתמלל, רגע...")
                return
            if self.state == STATE_RECORDING:
                self._stop_and_transcribe()
            elif self.state in (STATE_IDLE, STATE_ERROR):
                self._start_recording()

    def _start_recording(self):
        try:
            self.recorder.start()
            self._set_state(STATE_RECORDING)
        except Exception as e:
            self._set_state(STATE_ERROR)
            self.error_occurred.emit(f"כשל בהקלטה: {e}")

    def _stop_and_transcribe(self):
        audio_path = self.recorder.stop()
        if not audio_path:
            self.info_changed.emit("לא נקלט אודיו")
            self._set_state(STATE_IDLE)
            return

        self._set_state(STATE_TRANSCRIBING)

        def _work():
            try:
                raw = self.transcriber.transcribe(audio_path, self.config["language"])
                processed = self.processor.process(raw, self.config["language"])
                self.transcription_done.emit(raw, processed)
                if processed:
                    paste_text(processed)
            except Exception as e:
                self.error_occurred.emit(f"שגיאת תמלול: {e}")
            finally:
                try:
                    os.unlink(audio_path)
                except Exception:
                    pass
                self._set_state(STATE_IDLE)

        threading.Thread(target=_work, daemon=True).start()

    def update_config(self, new_values):
        old_model = self.config.get("model_size")
        old_device = self.config.get("device")
        self.config.update(new_values)
        save_config(self.config)
        self.processor = TextProcessor(self.config)

        if (
            new_values.get("model_size", old_model) != old_model
            or new_values.get("device", old_device) != old_device
        ):
            self.reload_transcriber()

    def _set_state(self, state):
        self.state = state
        self.state_changed.emit(state)
