"""
main.py

Now with real commands: record -> transcribe -> dispatch -> speak the result.
"""


from pynput import keyboard
from core.audio_io import record_and_transcribe, speak
from core.dispatcher import dispatch
import json

SETTINGS_PATH = "config/settings.json"

try:
    with open(SETTINGS_PATH) as f:
        settings = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    settings = {}



def on_activate():
    try:
        #print("Hotkey pressed - listening...")
        result = record_and_transcribe()
        print("You:", result)
        if not result:
            speak("I didn't catch that")
            return
        response = dispatch(result)
        print("Rose:", response)
        speak(response)
    except Exception as e:
        print("ERROR in on_activate:", e)


hotkey_combo = settings.get("hotkey", "<cmd>+<shift>+0")
hotkey = keyboard.GlobalHotKeys({hotkey_combo: on_activate})
hotkey.start()
hotkey.join()