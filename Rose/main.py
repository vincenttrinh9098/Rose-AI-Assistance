"""
main.py

Now with real commands: record -> transcribe -> dispatch -> speak the result.
"""


"""
main.py - hotkey-triggered voice assistant, suitable for background/launchd operation.
"""

from pynput import keyboard
from core.audio_io import record_and_transcribe, speak
from core.dispatcher import dispatch


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


hotkey = keyboard.GlobalHotKeys({'<cmd>+<shift>+0': on_activate})
hotkey.start()
hotkey.join()