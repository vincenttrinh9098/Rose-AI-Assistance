"""
main.py

Now with real commands: record -> transcribe -> dispatch -> speak the result.
"""

from core.audio_io import record_and_transcribe, speak
from core.dispatcher import dispatch

def main():
    print("Rose loopback test. Press Enter to record, Ctrl+C to quit.")
    
    while True:
        input()

        result = record_and_transcribe()
        print(result)

        if result == '':
            speak("Error no message")
            continue
        else:
            # Step 1: instead of speaking `result` directly (the raw transcription),
            # pass it into dispatch() to get back a response string, then speak THAT
            response = dispatch(result)
            speak(response)


if __name__ == "__main__":
    main()