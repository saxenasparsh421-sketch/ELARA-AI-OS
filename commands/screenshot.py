import os
from datetime import datetime

import pyautogui


def handle_screenshot(text):

    text = text.lower()

    if "screenshot" not in text:
        return None

    # Project root
    project_root = os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )

    screenshot_folder = os.path.join(
        project_root,
        "data",
        "screenshots"
    )

    os.makedirs(screenshot_folder, exist_ok=True)

    filename = datetime.now().strftime(
        "Screenshot_%Y%m%d_%H%M%S.png"
    )

    path = os.path.join(
        screenshot_folder,
        filename
    )

    image = pyautogui.screenshot()

    image.save(path)

    return "Screenshot captured, Boss."