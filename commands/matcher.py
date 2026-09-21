from commands.database import COMMANDS


def find_command(text):

    text = text.lower()

    for command, data in COMMANDS.items():

        for keyword in data["keywords"]:

            if keyword in text:
                return command

    return None