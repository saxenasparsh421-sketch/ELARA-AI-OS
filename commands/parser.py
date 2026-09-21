ACTION_WORDS = [
    "open",
    "launch",
    "start",
    "run"
]


def normalize(text):

    text = text.lower().strip()

    replacements = [
        "please",
        "can you",
        "could you",
        "would you",
        "boss",
        "my"
    ]

    for word in replacements:
        text = text.replace(word, "")

    while "  " in text:
        text = text.replace("  ", " ")

    return text.strip()


def contains_action(text):

    text = normalize(text)

    for word in ACTION_WORDS:
        if word in text:
            return True

    return False