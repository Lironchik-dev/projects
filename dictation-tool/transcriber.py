import sys
import ctypes

from faster_whisper import WhisperModel


def _cuda_visible():
    try:
        import ctranslate2
        return ctranslate2.get_cuda_device_count() > 0
    except Exception:
        return False


def _cublas_loadable():
    if sys.platform != "win32":
        return True
    for dll_name in ("cublas64_12.dll", "cublas64_11.dll"):
        try:
            ctypes.CDLL(dll_name)
            return True
        except OSError:
            continue
    return False


def _cudnn_loadable():
    if sys.platform != "win32":
        return True
    for dll_name in ("cudnn64_9.dll", "cudnn64_8.dll", "cudnn_ops_infer64_8.dll"):
        try:
            ctypes.CDLL(dll_name)
            return True
        except OSError:
            continue
    return False


def _can_use_cuda():
    if not _cuda_visible():
        return False, "no CUDA-capable device detected"
    if not _cublas_loadable():
        return False, "cuBLAS DLL not found (install nvidia-cublas-cu12)"
    if not _cudnn_loadable():
        return False, "cuDNN DLL not found (install nvidia-cudnn-cu12)"
    return True, ""


def _load_model(model_size, device, compute_type):
    print(f"[Transcriber] Loading '{model_size}' on {device} ({compute_type})...")
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    print(f"[Transcriber] Loaded on {device}.")
    return model


class Transcriber:
    def __init__(self, model_size="large-v3", device_pref="auto"):
        self.model_size = model_size
        self.model = None
        self.device = None

        if device_pref == "cpu":
            self._load_cpu()
            return

        if device_pref in ("auto", "cuda"):
            ok, reason = _can_use_cuda()
            if ok:
                try:
                    self.model = _load_model(model_size, "cuda", "float16")
                    self.device = "cuda"
                    return
                except Exception as e:
                    print(f"[Transcriber] CUDA load failed: {e}")
                    print("[Transcriber] Falling back to CPU.")
            else:
                print(f"[Transcriber] CUDA unavailable: {reason}")
                print("[Transcriber] Using CPU instead.")

        self._load_cpu()

    def _load_cpu(self):
        self.model = _load_model(self.model_size, "cpu", "int8")
        self.device = "cpu"
        print("[Transcriber] Running on CPU. Slower but works without CUDA libs.")
        print("[Transcriber] For GPU acceleration: pip install nvidia-cublas-cu12 nvidia-cudnn-cu12")

    def _do_transcribe(self, audio_path, language):
        segments, _info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        return " ".join(segment.text.strip() for segment in segments).strip()

    def transcribe(self, audio_path, language="he"):
        try:
            return self._do_transcribe(audio_path, language)
        except Exception as e:
            err = str(e).lower()
            cuda_lib_err = any(s in err for s in ("cublas", "cudnn", "cuda", "is not found or cannot be loaded"))
            if self.device == "cuda" and cuda_lib_err:
                print(f"[Transcriber] CUDA runtime error: {e}")
                print("[Transcriber] Falling back to CPU and retrying...")
                self._load_cpu()
                return self._do_transcribe(audio_path, language)
            raise
