"""
core/audio_io.py

record_and_transcribe(): mic -> text
speak(text): text -> audio out
"""

import sounddevice as sd
import soundfile as sf
import tempfile
from faster_whisper import WhisperModel
import pyttsx3

# TODO: load the Whisper model once here, at import time (not inside the function -
# loading it per-call would be slow). Look at WhisperModel(...) params: model size ("base"
# is a good starting point), device, compute_type.
_model = ...

# TODO: init pyttsx3 engine once here too
_tts_engine = ...


def record_and_transcribe(duration_seconds: int = 4, samplerate: int = 16000) -> str:
    """Records from the default mic for `duration_seconds`, returns transcribed text."""
    # 1. Use sd.rec(...) to record `duration_seconds` worth of audio at `samplerate`
    # 2. sd.wait() to block until recording is done
    # 3. Write it to a temp .wav file with sf.write(...)
    # 4. Pass that file path into _model.transcribe(...)
    # 5. transcribe() returns a generator of segments - join their .text together
    # 6. Return the joined string
    pass


def speak(text: str) -> None:
    """Speaks `text` out loud using local TTS."""
    # pyttsx3: .say(text) then .runAndWait()
    pass