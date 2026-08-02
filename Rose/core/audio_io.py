"""
core/audio_io.py
record_and_transcribe(): mic -> text
speak(text): text -> audio out
"""
import sounddevice as sd
import soundfile as sf
import tempfile
from faster_whisper import WhisperModel
import numpy as np
import json
import platform
import subprocess
import os
import signal
import threading
from core.paths import path_for
import time

SETTINGS_PATH = path_for("config", "settings.json")

try:
    with open(SETTINGS_PATH) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

_model = WhisperModel(model_size_or_path="tiny", device="cpu", compute_type="int8")

_current_speech_process = None


_cancel_recording = threading.Event()


def cancel_recording() -> None:
    print("cancel_recording() called")
    _cancel_recording.set()


def record_and_transcribe(samplerate: int = 16000) -> str:
    """Records from the default mic for `duration_seconds`, returns transcribed text."""
    audio = _record_until_silence()
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    sf.write(tmp.name, audio, samplerate)
    segments, info = _model.transcribe(tmp.name)
    result = " ".join(segment.text for segment in segments)
    return result






def _record_until_silence(
    samplerate: int = 16000,
    chunk_duration: float = 0.1,
    silence_threshold: float = 0.015,
    silence_limit: float = 1.25,
    max_duration: float = 10.0,
) -> np.ndarray:
    _cancel_recording.clear()
    print(">>> A: cleared cancel flag")

    chunk_samples = int(chunk_duration * samplerate)
    recorded_chunks = []
    speech_started = False
    silence_elapsed = 0.0
    total_elapsed = 0.0

    print(">>> B: about to create InputStream")
    stream = sd.InputStream(samplerate=samplerate, channels=1, dtype="float32")
    print(">>> C: InputStream created, about to start")
    stream.start()
    print(">>> D: stream started")
    print("Listening...")

    loop_count = 0
    while True:
        loop_count += 1
        print(f">>> E: loop iteration {loop_count}, about to check cancel")
        if _cancel_recording.is_set():
            print("Cancellation detected, breaking")
            break

        print(f">>> F: loop {loop_count}, about to read")
        data, overflowed = stream.read(chunk_samples)
        print(f">>> G: loop {loop_count}, read complete")

        chunk_volume = np.sqrt(np.mean(data**2))
        recorded_chunks.append(data)

        if chunk_volume > silence_threshold:
            speech_started = True
            silence_elapsed = 0
        elif chunk_volume < silence_threshold and speech_started:
            silence_elapsed += chunk_duration

        total_elapsed += chunk_duration

        if speech_started and silence_elapsed >= silence_limit:
            break
        elif total_elapsed >= max_duration:
            break

    print(">>> H: loop exited, stopping stream")
    stream.stop()
    time.sleep(0.05)
    stream.close()
    print(">>> I: stream closed")

    if not recorded_chunks:
        return np.array([])

    result = np.concatenate(recorded_chunks, axis=0)
    print(">>> J: returning result")
    return result







import os
PID_PATH = path_for("logs", "speaking_pid.json")
def speak(text: str) -> None:
    global _current_speech_process
    if platform.system() == "Darwin":
        args = ["say"]
        voice_name = settings.get("say_voice_name")
        if voice_name:
            check = subprocess.run(["say", "-v", "?"], capture_output=True, text=True)
            available = voice_name in check.stdout
            if available:
                args += ["-v", voice_name]
        args.append(text)
        _current_speech_process = subprocess.Popen(args)

        with open(PID_PATH, "w") as f:
            json.dump({"pid": _current_speech_process.pid}, f)

        _current_speech_process.wait()

def stop_speaking() -> None:
    """Interrupts any currently playing speech."""
    global _current_speech_process
    if platform.system() == "Darwin":
        if _current_speech_process and _current_speech_process.poll() is None:
            _current_speech_process.terminate()
    elif platform.system() == "Windows":
        # TODO: Windows implementation
        pass



def kill_any_speech() -> None:
    """Interrupts speech regardless of which process spawned it, using direct signal delivery
    instead of subprocess/pkill, to avoid CoreFoundation fork-safety issues."""
    try:
        with open(PID_PATH) as f:
            pid = json.load(f).get("pid")
        if pid:
            os.kill(pid, signal.SIGTERM)
    except (FileNotFoundError, ProcessLookupError, json.JSONDecodeError):
        pass