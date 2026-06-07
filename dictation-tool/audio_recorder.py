import sounddevice as sd
import numpy as np
import wave
import tempfile

SAMPLE_RATE = 16000


class AudioRecorder:
    def __init__(self):
        self.recording = False
        self.audio_chunks = []
        self.stream = None

    def _callback(self, indata, frames, time_info, status):
        if self.recording:
            self.audio_chunks.append(indata.copy())

    def start(self):
        if self.recording:
            return
        self.recording = True
        self.audio_chunks = []
        self.stream = sd.InputStream(
            samplerate=SAMPLE_RATE,
            channels=1,
            callback=self._callback,
            dtype="float32",
        )
        self.stream.start()

    def stop(self):
        if not self.recording:
            return None
        self.recording = False

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if not self.audio_chunks:
            return None

        audio = np.concatenate(self.audio_chunks, axis=0)

        temp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
        temp_path = temp.name
        temp.close()

        with wave.open(temp_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(SAMPLE_RATE)
            audio_int16 = (audio * 32767).astype(np.int16)
            wf.writeframes(audio_int16.tobytes())

        return temp_path
