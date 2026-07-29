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
import numpy as np
import json


SETTINGS_PATH = "config/settings.json"

try:
    with open(SETTINGS_PATH) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}


_model = WhisperModel(model_size_or_path="base", device="cpu", compute_type="int8")
_tts_engine = pyttsx3.init()
if(settings.get("voice_id")):
    _tts_engine.setProperty('voice', settings.get("voice_id"))


def record_and_transcribe(samplerate: int = 16000) -> str:
    """Records from the default mic for `duration_seconds`, returns transcribed text."""


    audio = _record_until_silence()


    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, samplerate)


    segments, info = _model.transcribe(tmp.name)

    result = " ".join( segment.text for segment in segments)
    return result


def _record_until_silence(
    samplerate: int = 16000,
    chunk_duration: float = 0.1,
    silence_threshold: float = 0.01,
    silence_limit: float = 1.5,
    max_duration: float = 15.0,
) -> np.ndarray:
    """Records audio until the user stops talking, returns the full recording as a numpy array."""

    chunk_samples = int(chunk_duration * samplerate)
    recorded_chunks = []
    speech_started = False
    silence_elapsed = 0.0
    total_elapsed = 0.0

    stream = sd.InputStream(samplerate=samplerate, channels=1, dtype="float32")
    stream.start()

    print("Listening...")

    while True:
        data, overflowed = stream.read(chunk_samples)

        chunk_volume = np.sqrt(np.mean(data**2))

        recorded_chunks.append(data)


        if(chunk_volume>silence_threshold):
            speech_started = True
            silence_elapsed = 0
        elif(chunk_volume<silence_threshold and speech_started):
            silence_elapsed+=chunk_duration

        total_elapsed+=chunk_duration

  
        if(speech_started and silence_elapsed>=silence_limit):
            break
        elif(total_elapsed>=max_duration):
            break

        pass

    stream.stop()
    stream.close()

    result = np.concatenate(recorded_chunks,axis=0)
    return result

def speak(text: str) -> None:
    """Speaks `text` out loud using local TTS."""
    _tts_engine.say(text)
    _tts_engine.runAndWait()
