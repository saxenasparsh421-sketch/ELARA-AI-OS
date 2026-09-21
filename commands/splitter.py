import re

# Words that usually start a command
VERBS = [
    "open",
    "launch",
    "start",
    "run",
    "close"
]


def split_commands(text: str) -> list[str]:
    """
    Split multiple spoken commands into individual commands.

    Example:
        Open Chrome and YouTube
        ->
        ["Open Chrome", "Open YouTube"]
    """

    text = text.strip()
    import re

    # Remove a trailing "and"
    text = re.sub(r"\band\s*$", "", text, flags=re.IGNORECASE)

    if not text:
        return []

    # Split by 'and'
    parts = re.split(r",|\band\b", text, flags=re.IGNORECASE)

    commands = []

    current_verb = None

    for part in parts:

        part = part.strip()

        if not part:
            continue

        words = part.split()

        if not words:
            continue

        first = words[0].lower()

        # New command starts with a verb
        if first in VERBS:
            current_verb = words[0]
            commands.append(part)

        else:
            # Inherit previous verb
            if current_verb:
                commands.append(f"{current_verb} {part}")
            else:
                commands.append(part)

    return commands