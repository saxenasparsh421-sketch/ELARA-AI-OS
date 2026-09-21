"""
commands/router.py

Main command router for ELARA OS
"""

from ai.nlp import process

from commands.memory import handle_memory
from commands.study import handle_study
from commands.weather import handle_weather

from commands.apps import handle_apps
from commands.websites import handle_websites
from commands.system import execute as handle_system
from commands.search import handle_search
from commands.folders import handle_folders
from commands.screenshot import handle_screenshot
from commands.screen_vision import handle_screen_vision
from commands.ocr import handle_ocr


def route(text, speech=None):

    result = handle_screen_vision(
        text,
        speech
    )

    if result:
        return result

    result = handle_ocr(
        text,
        speech
    )

    if result:
        return result

    result = handle_memory(text)

    if result:
        return result

    result = handle_study(text)

    if result:
        return result

    result = handle_weather(text)

    if result:
        return result

    data = process(text)

    intent = data["intent"]
    entity = data["entity"]

    if intent in [
        "SEARCH_GOOGLE",
        "SEARCH_YOUTUBE"
    ]:

        result = handle_search(text)

        if result:
            return result

    if intent == "OPEN_APP":

        result = handle_apps(entity)

        if result:
            return result

        result = handle_websites(entity)

        if result:
            return result

    if intent == "SCREENSHOT":

        result = handle_screenshot(text)

        if result:
            return result

    if intent == "SYSTEM":

        result = handle_system(text)

        if result:
            return result

    result = handle_folders(text)

    if result:
        return result

    result = handle_apps(text)

    if result:
        return result

    result = handle_websites(text)

    if result:
        return result

    result = handle_system(text)

    if result:
        return result

    return None