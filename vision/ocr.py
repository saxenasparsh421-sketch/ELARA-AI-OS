"""
ELARA OCR
Local screen OCR with position and region support.

Uses Tesseract locally.
No OpenRouter or cloud AI is used.
"""

from pathlib import Path

import pytesseract
from PIL import Image


class OCR:

    def __init__(self):

        self.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

        if Path(self.tesseract_cmd).exists():

            pytesseract.pytesseract.tesseract_cmd = (
                self.tesseract_cmd
            )

    # =====================================================
    # BASIC OCR
    # =====================================================

    def read(self, image_path):

        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_path)

        text = pytesseract.image_to_string(
            image
        )

        return text.strip()

    # =====================================================
    # POSITION-AWARE OCR
    # =====================================================

    def read_data(self, image_path):

        """
        Read OCR text together with position
        and confidence information.
        """

        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_path)

        return self.read_image_data(image)

    # =====================================================
    # OCR DIRECTLY FROM PIL IMAGE
    # =====================================================

    def read_image_data(self, image):

        data = pytesseract.image_to_data(
            image,
            output_type=pytesseract.Output.DICT
        )

        results = []

        total_items = len(
            data["text"]
        )

        for index in range(total_items):

            text = data["text"][index].strip()

            if not text:
                continue

            try:

                confidence = float(
                    data["conf"][index]
                )

            except (
                ValueError,
                TypeError
            ):

                confidence = -1

            results.append(
                {
                    "text": text,
                    "confidence": confidence,

                    "left": int(
                        data["left"][index]
                    ),

                    "top": int(
                        data["top"][index]
                    ),

                    "width": int(
                        data["width"][index]
                    ),

                    "height": int(
                        data["height"][index]
                    ),

                    "block_num": int(
                        data["block_num"][index]
                    ),

                    "par_num": int(
                        data["par_num"][index]
                    ),

                    "line_num": int(
                        data["line_num"][index]
                    ),
                }
            )

        return results

    # =====================================================
    # REGION OCR
    # =====================================================

    def read_region(
        self,
        image_path,
        left,
        top,
        right,
        bottom
    ):

        """
        Crop a specific screen region and
        perform OCR on that region.

        Coordinates are in pixels.
        """

        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(
            image_path
        )

        cropped = image.crop(
            (
                left,
                top,
                right,
                bottom
            )
        )

        return self.read_image_data(
            cropped
        )


ocr = OCR()