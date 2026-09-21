"""
ai/memory_engine.py

JARVIS Memory Engine
"""

import json
import os


class MemoryEngine:

    def __init__(self):

        self.file = "data/memory/memory.json"

        self.memory = {}

        self.load()


    # -----------------------------
    # Load Memory
    # -----------------------------

    def load(self):

        folder = os.path.dirname(self.file)

        os.makedirs(
            folder,
            exist_ok=True
        )

        if not os.path.exists(self.file):

            self.memory = {}

            self.save()

            return


        try:

            with open(
                self.file,
                "r",
                encoding="utf-8"
            ) as f:

                self.memory = json.load(f)


        except json.JSONDecodeError:

            print("Memory file corrupted. Resetting...")

            self.memory = {}

            self.save()



    # -----------------------------
    # Save Memory
    # -----------------------------

    def save(self):

        with open(
            self.file,
            "w",
            encoding="utf-8"
        ) as f:

            json.dump(
                self.memory,
                f,
                indent=4
            )



    # -----------------------------
    # Remember Something
    # -----------------------------

    def remember(
        self,
        key,
        value
    ):

        self.memory[key] = value

        self.save()



    # -----------------------------
    # Recall Something
    # -----------------------------

    def recall(
        self,
        key
    ):

        return self.memory.get(key)



    # -----------------------------
    # Forget Something
    # -----------------------------

    def forget(
        self,
        key
    ):

        if key in self.memory:

            del self.memory[key]

            self.save()

            return True

        return False



    # -----------------------------
    # Get All Memories
    # -----------------------------

    def all(self):

        return self.memory



    # -----------------------------
    # Clear Everything
    # -----------------------------

    def clear(self):

        self.memory = {}

        self.save()