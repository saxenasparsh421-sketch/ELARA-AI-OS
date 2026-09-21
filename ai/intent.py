import re

# Higher priority intents should come first
INTENTS = [
    (
        "SEARCH_YOUTUBE",
        [
            "youtube",
            "yt",
        ],
    ),
    (
        "SEARCH_GOOGLE",
        [
            "search",
            "google",
            "find",
            "look up",
        ],
    ),
    (
        "OPEN_APP",
        [
            "open",
            "launch",
            "run",
            "start",
        ],
    ),
    (
        "SCREENSHOT",
        [
            "screenshot",
            "screen shot",
            "capture screen",
        ],
    ),
    (
        "SYSTEM",
        [
            "shutdown",
            "restart",
            "sleep",
            "lock",
        ],
    ),
]


def detect_intent(text):
    """
    Detect the user's intent from a sentence.
    """

    text = text.lower().strip()

    # -----------------------------
    # YouTube has highest priority
    # -----------------------------
    if re.search(r"\byoutube\b", text):
        return "SEARCH_YOUTUBE"

    if re.search(r"\byt\b", text):
        return "SEARCH_YOUTUBE"

    # -----------------------------
    # Check remaining intents
    # -----------------------------
    for intent, keywords in INTENTS:

        for keyword in keywords:

            pattern = r"\b" + re.escape(keyword) + r"\b"

            if re.search(pattern, text):
                return intent

    return "UNKNOWN"