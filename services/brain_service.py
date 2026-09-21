"""
ELARA Brain Service
OpenRouter only
"""

import os
from typing import Any

from dotenv import load_dotenv

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


load_dotenv()


class BrainService:

    OPENROUTER_URL = "https://openrouter.ai/api/v1"

    OPENROUTER_MODEL = os.getenv(
        "OPENROUTER_MODEL",
        "openrouter/free"
    )

    OPENROUTER_API_KEY = os.getenv(
        "OPENROUTER_API_KEY",
        ""
    )

    SYSTEM_PROMPT = """
You are ELARA, a desktop AI assistant created for Mister Sparsh.

Your name is ELARA.

If asked your name:
My name is ELARA.

If asked who you are:
I am ELARA. I was created by Mister Sparsh.

Be concise, useful and natural.

You are connected to a desktop assistant system.
Do not pretend to have performed an action unless the local system actually performed it.
"""

    def __init__(self):
        print("Initializing Brain Service...")

        self.client = None
        self.backend = "OPENROUTER"

        if OpenAI is None:
            raise RuntimeError(
                "The 'openai' package is not installed."
            )

        if not self.OPENROUTER_API_KEY:
            raise RuntimeError(
                "OPENROUTER_API_KEY is missing."
            )

        try:
            self.client = OpenAI(
                api_key=self.OPENROUTER_API_KEY,
                base_url=self.OPENROUTER_URL
            )

            print("[BRAIN] OpenRouter ready.")
            print(
                "[BRAIN] Model:",
                self.OPENROUTER_MODEL
            )
            print("[BRAIN] Service ready.")

        except Exception as error:
            print(
                "[BRAIN] OpenRouter initialization failed:",
                error
            )
            raise

    # =====================================================
    # MAIN AI
    # =====================================================

    def think(self, prompt: str) -> str:

        prompt = str(
            prompt
        ).strip()

        if not prompt:
            return (
                "Please give me a command, Boss."
            )

        try:
            response = self.ask_openrouter(
                prompt
            )

            if response:
                print(
                    "[BRAIN] Response backend: OpenRouter"
                )

                return response

        except Exception as error:

            print(
                "[BRAIN] OpenRouter error:",
                error
            )

            return (
                "I couldn't reach the OpenRouter AI service "
                "right now, Boss."
            )

        return (
            "OpenRouter returned no usable response, Boss."
        )

    # =====================================================
    # OPENROUTER REQUEST
    # =====================================================

    def ask_openrouter(
        self,
        prompt: str
    ) -> str:

        if self.client is None:
            raise RuntimeError(
                "OpenRouter client is not initialized."
            )

        print(
            "[BRAIN] Sending request to OpenRouter..."
        )

        response: Any = (
            self.client
            .chat
            .completions
            .create(
                model=self.OPENROUTER_MODEL,

                messages=[
                    {
                        "role": "system",
                        "content": self.SYSTEM_PROMPT
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],

                temperature=0.7,

                max_tokens=700
            )
        )

        if not response:
            raise RuntimeError(
                "OpenRouter returned no response."
            )

        choices = getattr(
            response,
            "choices",
            None
        )

        if not choices:
            raise RuntimeError(
                "OpenRouter returned no choices."
            )

        message = getattr(
            choices[0],
            "message",
            None
        )

        if message is None:
            raise RuntimeError(
                "OpenRouter response has no message."
            )

        content = getattr(
            message,
            "content",
            None
        )

        if content is None:
            raise RuntimeError(
                "OpenRouter returned empty content."
            )

        content = str(
            content
        ).strip()

        if not content:
            raise RuntimeError(
                "OpenRouter returned blank content."
            )

        return content

    # =====================================================
    # BACKEND NAME
    # =====================================================

    def get_backend(self) -> str:
        return self.backend


# =========================================================
# DIRECT TEST
# =========================================================

if __name__ == "__main__":

    brain = BrainService()

    print(
        "\nBackend:",
        brain.get_backend()
    )

    print(
        "\nELARA:",
        brain.think(
            "Hello, introduce yourself."
        )
    )