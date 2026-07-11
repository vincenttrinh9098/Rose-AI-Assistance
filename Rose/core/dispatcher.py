"""
core/dispatcher.py

Takes transcribed text, decides which command function to call, calls it.
Nothing in here knows HOW a command works - only WHICH one to run.
"""

from commands.browser import open_youtube, open_google, search_google


def dispatch(text: str) -> str:
    """
    Given transcribed text, run the matching command.
    Returns a string to be spoken back to the user (confirmation or error).
    """
    text = text.lower()


    if "open youtube" in text:
        open_youtube()
        return "Opening up youtube right now for you"
    elif "open google" in text:
        open_google()
        return "Opening up google right now for you"
    elif "search google" in text:
        words = text.split()

        if "for" in words:
            index = words.index("for")
            query = " ".join(words[index+1:])
        else:
            # assume everything after google is the query
            index = words.index("google")
            query = " ".join(words[index+1:])

        search_google(query)
        return "Searching on google.." 
    else:
        return ("Sorry, I didn't quite get that...")



    pass