from ai.memory_engine import MemoryEngine


memory = MemoryEngine()


def handle_memory(text):

    text = text.lower().strip()


    # -----------------------------
    # Remember
    # -----------------------------
    if text.startswith("remember"):

        data = text.replace(
            "remember",
            "",
            1
        ).strip()


        if " is " in data:

            key, value = data.split(
                " is ",
                1
            )

            key = key.replace(
                "my ",
                ""
            ).strip()


            memory.remember(
                key,
                value
            )


            return "I will remember that, Boss."


    # -----------------------------
    # Recall
    # -----------------------------
    if text.startswith("what is my"):

        key = text.replace(
            "what is my",
            "",
            1
        ).strip()


        result = memory.recall(key)


        if result:

            return f"Your {key} is {result}, Boss."


        return f"I don't remember your {key}, Boss."


    # -----------------------------
    # Forget
    # -----------------------------
    if text.startswith("forget my"):

        key = text.replace(
            "forget my",
            "",
            1
        ).strip()


        if memory.forget(key):

            return f"I forgot your {key}, Boss."


    return None