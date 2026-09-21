import re


def extract_entity(text, intent):

    text = text.lower()

    if intent == "OPEN_APP":

        prefixes = [
            "open",
            "launch",
            "run",
            "start",
        ]

        for p in prefixes:
            if text.startswith(p):
                return text[len(p):].strip()

    elif intent == "SEARCH_GOOGLE":

        text = re.sub(
            r"(search|google|find|look up)",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = text.replace("for", "")

        return text.strip()

    elif intent == "SEARCH_YOUTUBE":

        text = text.replace("youtube", "")
        text = text.replace("yt", "")
        text = text.replace("search", "")
        text = text.replace("for", "")

        return text.strip()

    return ""