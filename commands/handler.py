from commands.router import route
from commands.splitter import split_commands


def handle(text):

    commands = split_commands(text)

    responses = []

    for command in commands:

        result = route(command)

        if result:
            responses.append(result)

    if responses:
        return "\n".join(responses)

    return None