"""
ELARA Screen Vision
Screenshot analysis through OpenRouter.
"""

import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


PROJECT_ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

load_dotenv(ENV_FILE, override=True)


class ScreenVision:

    def __init__(self):

        api_key = os.environ.get("OPENROUTER_API_KEY")

        if not api_key:
            raise RuntimeError(
                f"OPENROUTER_API_KEY is not set.\n"
                f"Checked .env at: {ENV_FILE}"
            )

        self.model = os.environ.get(
            "OPENROUTER_VISION_MODEL",
            "openrouter/free"
        )

        self.client = OpenAI(
            api_key=api_key,
            base_url="https://openrouter.ai/api/v1"
        )

    def analyze(self, image_path, prompt):
        """
        Analyze a local screenshot using OpenRouter vision.
        """

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Screenshot not found: {image_path}"
            )

        image_bytes = image_path.read_bytes()

        encoded_image = base64.b64encode(
            image_bytes
        ).decode("utf-8")

        suffix = image_path.suffix.lower()

        mime_types = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif",
        }

        mime_type = mime_types.get(
            suffix,
            "image/png"
        )

        response = self.client.chat.completions.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are ELARA's screen vision system. "
                        "Analyze the provided computer screenshot "
                        "carefully. Identify visible applications, "
                        "UI elements, text, errors, buttons and "
                        "other relevant information. "
                        "Only describe information that is actually "
                        "visible. Do not invent details."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt,
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": (
                                    f"data:{mime_type};base64,"
                                    f"{encoded_image}"
                                )
                            },
                        },
                    ],
                },
            ],
        )

        return (
            response.choices[0]
            .message
            .content
            or ""
        ).strip()


screen_vision = ScreenVision()