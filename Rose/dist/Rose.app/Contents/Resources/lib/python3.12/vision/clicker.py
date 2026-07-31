"""
vision/clicker.py

Takes coordinates (from locator.py) and actually moves/clicks the mouse there.
Handles Retina scaling - Claude's coordinates are based on the screenshot's
pixel size, but pyautogui expects logical screen coordinates.
"""

import pyautogui
from PIL import Image


def click_at(x: int, y: int, image_path: str) -> None:
    """
    Moves the mouse to (x, y) and clicks, converting from screenshot pixel
    coordinates to logical screen coordinates first.
    """

    # TODO: get the actual screenshot's pixel size using PIL
    # Image.open(image_path).size returns (width, height) as a tuple
    image_width, image_height = Image.open(image_path).size
    
    # TODO: get pyautogui's logical screen size
    # pyautogui.size() returns a Size object - it can be unpacked like a tuple too
    screen_width, screen_height = pyautogui.size()

    # TODO: calculate the scaling ratio (image size / screen size)
    # this should come out to 2.0 on your machine based on what we just measured
    scale_x = image_width/screen_width
    scale_y = image_height/screen_height

    # TODO: divide the incoming x, y by the scale factors to convert to logical coordinates
    real_x = x/scale_x
    real_y = y/scale_y

    # TODO: click at the converted coordinates
    pyautogui.click(real_x, real_y)