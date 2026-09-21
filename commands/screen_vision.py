import re

from vision.screen import screen_capture
from vision.screen_vision import screen_vision


CORRECTIONS = {
    "deco": "dekho",
    "deko": "dekho",
}


TRIGGERS = [
    "screen dekho",
    "screen ko dekho",
    "screen pe dekho",
    "screen par dekho",
    "screen check karo",
    "screen analyze karo",
    "screen analyse karo",

    "dekho",
    "dekhna",
    "zara dekho",
    "ye dekho",
    "isko dekho",
    "idhar dekho",

    "kya dikh raha hai",
    "kya dikh raha",
    "kya nazar aa raha hai",
    "kya nazar aa raha",

    "what do you see",
    "what can you see",
    "what is on my screen",
    "what's on my screen",
    "look at the screen",
    "look at my screen",
    "check the screen",
    "check my screen",
]


def normalize_text(text):

    text = text.lower().strip()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    words = text.split()

    fixed_words = []

    for word in words:

        fixed_words.append(
            CORRECTIONS.get(
                word,
                word
            )
        )

    return " ".join(fixed_words)


def is_vision_command(text):

    text = normalize_text(text)

    for trigger in TRIGGERS:

        if trigger in text:
            return True

    return False


def handle_screen_vision(text, speech=None):

    if not text:
        return None

    if not is_vision_command(text):
        return None

    try:

        print()
        print("[SCREEN VISION] Taking screenshot...")
        print()

        if speech:
            speech.speak(
                "Taking screenshot Boss."
            )

        screenshot_path = screen_capture.capture()

        print(
            "[SCREEN VISION] Screenshot:",
            screenshot_path
        )

        print()
        print("[SCREEN VISION] Analyzing screen...")
        print()

        if speech:
            speech.speak(
                "Analyzing the screen Boss."
            )

        prompt = (
            "Analyze this computer screenshot carefully. "
            "Tell me what is actually visible. "
            "Identify the active application, windows, "
            "important UI elements, visible text, "
            "errors and warnings. "
            "If code is visible, identify the relevant "
            "file and visible problem. "
            "Only describe things that are actually visible. "
            "Do not invent anything. "
            "Answer naturally as ELARA speaking to Boss. "
            "Keep the answer concise for voice."
        )

        result = screen_vision.analyze(
            screenshot_path,
            prompt
        )

        if not result:

            print(
                "[SCREEN VISION] No analysis result."
            )

            return (
                "I could not determine what is visible "
                "on the screen Boss."
            )

        print()
        print("[SCREEN VISION] Analysis complete.")
        print()

        return result

    except Exception as e:

        print(
            "[SCREEN VISION ERROR]",
            e
        )

        return (
            "I was unable to analyze the screen right now Boss."
        )