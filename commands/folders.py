import os
import subprocess


HOME = os.path.expanduser("~")

FOLDERS = {
    "desktop": os.path.join(HOME, "Desktop"),
    "downloads": os.path.join(HOME, "Downloads"),
    "documents": os.path.join(HOME, "Documents"),
    "pictures": os.path.join(HOME, "Pictures"),
    "videos": os.path.join(HOME, "Videos"),
    "music": os.path.join(HOME, "Music"),
}


def handle_folders(text):

    text = text.lower()

    for folder, path in FOLDERS.items():

        if folder in text:

            subprocess.Popen(f'explorer "{path}"')

            return f"Opening {folder.title()}, Boss."

    return None