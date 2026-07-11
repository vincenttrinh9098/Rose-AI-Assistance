"""
main.py

Task 1: prove the pipeline works. No command parsing yet.
Press Enter -> talk -> Rose repeats back what it heard.
"""

from core.audio_io import record_and_transcribe, speak

def main():
    print("Rose loopback test. Press Enter to record, Ctrl+C to quit.")
    
    while True:
    # Step 1: pause and wait for the user to press Enter before recording
    # hint: input() blocks until Enter is pressed - you don't need to store what they type
        input()

        # Step 2: call record_and_transcribe() and store the result
        result = record_and_transcribe()
        # Step 3: print what was heard, so you can visually confirm it before it speaks
        print(result)

        # Step 4: handle the empty case - if nothing was transcribed (empty string),
        # speak an error message and skip back to the top of the loop (use `continue`)
        if(result==''):
            speak("Error no message")
            continue
        else: # Step 5: otherwise, speak the transcribed text back
            speak(result)

 

if __name__ == "__main__":
    main()