"""
core/wake_word.py

Listens continuously in small audio chunks and blocks until the wake word
is detected. Mirrors the chunked-streaming pattern from _record_until_silence.
"""

import numpy as np
import sounddevice as sd
from openwakeword.model import Model

# TODO: load the wake word model once at import time, same pattern as _model in audio_io.py
# Model(wakeword_models=["hey_jarvis"]) - openwakeword ships this one pretrained
_ww_model = Model(wakeword_models=["hey_jarvis", "alexa"], inference_framework="onnx")


def listen_for_wake_word(samplerate: int = 16000, chunk_size: int = 1280) -> None:
    """Blocks until the wake word is detected, then returns."""

    stream = sd.InputStream(samplerate=samplerate, channels=1, dtype="int16")
    stream.start()

    print("Listening for wake word...")

    while True:
        # Step 1: read one chunk from the stream (same pattern as _record_until_silence)
        # stream.read(chunk_size) returns (data, overflowed)
        data, overflowed = stream.read(chunk_size)

        # Step 2: openwakeword expects a 1D int16 numpy array, not the raw stream shape
        # data comes back as shape (chunk_size, 1) - flatten it with .flatten() or .reshape(-1)
        data = data.flatten()
        #print("max amplitude:", np.abs(data).max())

        # Step 3: run prediction - _ww_model.predict(audio_chunk) returns a dict
        # like {"hey_jarvis": 0.02} - a confidence score per wake word

        my_dict = _ww_model.predict(data) 
       # print(my_dict)
        # Step 4: check the score for "hey_jarvis" against a threshold (try 0.5 to start)
        # if it exceeds the threshold: break out of the loop
        for key, value in my_dict.items():
            if value > 0.5:
                stream.stop()
                stream.close()
                return

    stream.stop()
    stream.close()