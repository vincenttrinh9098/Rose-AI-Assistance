"""
main.py

Hotkey-triggered voice assistant, suitable for background/launchd operation.
Supports interrupting speech by pressing the hotkey again mid-response.
"""

import json
import queue
import threading
from pynput import keyboard
from core.audio_io import record_and_transcribe, speak, stop_speaking
from core.dispatcher import dispatch
from core.conversation_log import log_exchange
import random 
from core.status import set_status

SETTINGS_PATH = "config/settings.json"

print("Ready to begin...")
try:
    with open(SETTINGS_PATH) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}

task_queue = queue.Queue()
is_speaking = threading.Event()


buffering_responses = [
    "One moment...",
    "Just a second...",
    "Let me think...",
]


def on_activate():
    print(f"Hotkey pressed - is_speaking: {is_speaking.is_set()}")
    if is_speaking.is_set():
        print("Interrupting current speech")
        stop_speaking()
        is_speaking.clear()

    if task_queue.empty():
        print("Hotkey pressed")
        task_queue.put(True)



def process_tasks():
    while True:
        task_queue.get()
        set_status("listening")
        print("Listening...")
        result = record_and_transcribe()
        print("You:", result)

        if not result:
            is_speaking.set()
            set_status("speaking")
            speak("I didn't catch that")
            is_speaking.clear()
            set_status("idle")
            continue
        speak(random.choice(buffering_responses))
        response = dispatch(result)
        log_exchange(result, response)

        is_speaking.set()
        set_status("speaking")
        speak(response)
        is_speaking.clear()
        set_status("idle")
        
hotkey_combo = settings.get("hotkey", "<cmd>+<shift>+0")
hotkey = keyboard.GlobalHotKeys({hotkey_combo: on_activate})
hotkey.start()

process_tasks()



