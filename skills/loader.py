import importlib


SKILLS = [
    "apps",
    "websites",
    "system",
]


def load_skills():

    loaded = []

    for skill in SKILLS:

        module = importlib.import_module(f"commands.{skill}")

        loaded.append(module)

    return loaded