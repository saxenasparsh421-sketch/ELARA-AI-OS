from commands.memory import handle_memory


tests = [

    "Remember my favorite browser is Chrome",

    "What is my favorite browser",

    "Forget my favorite browser",

    "What is my favorite browser"

]


for command in tests:

    print("You:", command)

    print(
        "JARVIS:",
        handle_memory(command)
    )

    print("-" * 40)