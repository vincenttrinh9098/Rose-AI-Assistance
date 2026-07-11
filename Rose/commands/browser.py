"""
commands/browser.py

Functions that open things in the browser.
Each function should do ONE thing - the dispatcher decides *when* to call it,
this file only knows *how*.
"""

import webbrowser
import platform


os_name = platform.system()



def open_youtube():
    chrome = webbrowser.get("chrome")
    chrome.open("https://www.youtube.com")



def open_google():
    chrome = webbrowser.get("chrome")
    chrome.open("https://www.google.com")

def search_google(query: str):
    # TODO: open a Google search URL with `query` appended
    # hint: Google search URLs look like https://google.com/search?q=YOUR+QUERY+HERE
    # you'll need to handle spaces in `query` somehow before building the URL string
    filtered_query = query.replace(" ", "+")
    
    chrome = webbrowser.get("chrome")
    chrome.open(f"https://google.com/search?q={filtered_query}")
