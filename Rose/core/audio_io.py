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

# TODO: load the Whisper model once here, at import time
# WhisperModel(model_size, device=..., compute_type=...)
# - model_size: try "base" as a starting point
# - device: "cpu" (unless you have GPU support set up)
# - compute_type: "int8" is a good default for CPU - faster, smaller, less accurate than float
_model = WhisperModel(model_size_or_path="base", device="cpu", compute_type="int8")

# TODO: init pyttsx3 engine once here too
# pyttsx3 has an init() function that returns an engine object
_tts_engine = pyttsx3.init()


def record_and_transcribe(samplerate: int = 16000) -> str:
    """Records from the default mic for `duration_seconds`, returns transcribed text."""

    # Step 1: record audio
    # sd.rec() takes (num_frames, samplerate=, channels=, dtype=)
    # num_frames = duration_seconds * samplerate
    # use channels=1 (mono), dtype="float32"
    audio = _record_until_silence()

    # Step 3: write the audio to a temp .wav file
    # use tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp
    # then sf.write(tmp.name, audio, samplerate)
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, samplerate)

    # Step 4: transcribe it
    # _model.transcribe(path) returns (segments, info) - segments is a generator
    segments, info = _model.transcribe(tmp.name)

    # Step 5: join the segment texts into one string and return it
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
        # Step 1: read one chunk from the stream
        # stream.read(chunk_samples) returns (data, overflowed) - unpack both
        data, overflowed = stream.read(chunk_samples)

        # Step 2: calculate the volume of this chunk
        # RMS formula: sqrt(mean(data^2)) - use np.sqrt and np.mean
        chunk_volume = np.sqrt(np.mean(data**2))
        # Step 3: append this chunk's data to recorded_chunks regardless of volume
        # (we want silence in the middle of a sentence included, just not trailing silence)
        recorded_chunks.append(data)

        # Step 4: check volume against silence_threshold
        # - if above threshold: speech_started = True, reset silence_elapsed to 0
        # - if below threshold AND speech_started: add chunk_duration to silence_elapsed

        if(chunk_volume>silence_threshold):
            speech_started = True
            silence_elapsed = 0
        elif(chunk_volume<silence_threshold and speech_started):
            silence_elapsed+=chunk_duration

        # Step 5: increment total_elapsed by chunk_duration
        total_elapsed+=chunk_duration

        # Step 6: check stop conditions
        # - if speech_started and silence_elapsed >= silence_limit: break
        # - if total_elapsed >= max_duration: break (safety net so it can't run forever)
        if(speech_started and silence_elapsed>=silence_limit):
            break
        elif(total_elapsed>=max_duration):
            break

        pass

    stream.stop()
    stream.close()

    # Step 7: concatenate all chunks into a single numpy array and return it
    # np.concatenate(recorded_chunks, axis=0)
    result = np.concatenate(recorded_chunks,axis=0)
    return result

def speak(text: str) -> None:
    """Speaks `text` out loud using local TTS."""
    # pyttsx3: .say(text) then .runAndWait()
    pass