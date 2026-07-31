"""
vision/screenshot.py

Captures the screen and saves it as an image file, ready to hand to
Claude's vision capability or crop later.
"""

import pyautogui
import tempfile
import os
from datetime import datetime

def take_screenshot() -> str:
    """Captures the full screen, saves it to a temp file, returns the file path."""
    screenshot = pyautogui.screenshot() 

    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    screenshot.save(tmp.name) 

    return tmp.name



def take_screenshot_and_save(folder: str = "screenshots") -> str:
    """Captures the screen and saves it with a timestamped filename in `folder`."""
    
    # TODO: os.makedirs(folder, exist_ok=True) - creates the folder if it doesn't exist yet,
    # does nothing if it already exists (exist_ok=True prevents an error either way)
    os.makedirs(folder, exist_ok=True)

    # TODO: build a filename using the current timestamp so repeated screenshots don't overwrite each other
    # datetime.now().strftime("%Y%m%d_%H%M%S") gives you something like "20260713_143022"
    filename = datetime.now().strftime("%Y%m%d_%H%M%S") + ".png"

    # TODO: build the full path with os.path.join(folder, filename)
    path = os.path.join(folder,filename)

    # TODO: same pyautogui.screenshot() + .save(path) as before, just saving to this path instead of a tempfile
    pyautogui.screenshot().save(path)
    # TODO: return the path

    return path