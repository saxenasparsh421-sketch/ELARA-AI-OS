"""
ELARA Face Vision
Local face detection using OpenCV.
"""

from pathlib import Path

import cv2


PROJECT_ROOT = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    PROJECT_ROOT
    / "data"
    / "models"
    / "haarcascade_frontalface_default.xml"
)


class FaceVision:

    def __init__(self):

        if not MODEL_PATH.exists():

            raise FileNotFoundError(
                f"Face detection model not found: {MODEL_PATH}"
            )

        self.detector = cv2.CascadeClassifier(
            str(MODEL_PATH)
        )

        if self.detector.empty():

            raise RuntimeError(
                "Unable to load the face detection model."
            )

    # =====================================================
    # LOAD IMAGE
    # =====================================================

    def _load_image(self, image_path):

        image_path = Path(image_path)

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = cv2.imread(
            str(image_path)
        )

        if image is None:

            raise RuntimeError(
                "Unable to read the image."
            )

        return image

    # =====================================================
    # DETECT FACES IN LIVE FRAME
    # =====================================================

    def detect_frame(self, frame):

        if frame is None:

            raise ValueError(
                "Camera frame is empty."
            )

        gray = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        results = []

        for x, y, width, height in faces:

            results.append(
                {
                    "x": int(x),
                    "y": int(y),
                    "width": int(width),
                    "height": int(height),
                }
            )

        return results

    # =====================================================
    # DETECT FACES
    # =====================================================

    def detect(self, image_path):

        image = self._load_image(
            image_path
        )

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        results = []

        for x, y, width, height in faces:

            results.append(
                {
                    "x": int(x),
                    "y": int(y),
                    "width": int(width),
                    "height": int(height),
                }
            )

        return results

    # =====================================================
    # COUNT FACES
    # =====================================================

    def count(self, image_path):

        faces = self.detect(
            image_path
        )

        return len(faces)

    # =====================================================
    # DETECT + DRAW BOXES
    # =====================================================

    def detect_and_draw(
        self,
        image_path,
        output_path=None
    ):

        image = self._load_image(
            image_path
        )

        gray = cv2.cvtColor(
            image,
            cv2.COLOR_BGR2GRAY
        )

        faces = self.detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        detected_faces = []

        for x, y, width, height in faces:

            cv2.rectangle(
                image,
                (x, y),
                (x + width, y + height),
                (0, 255, 0),
                2
            )

            detected_faces.append(
                {
                    "x": int(x),
                    "y": int(y),
                    "width": int(width),
                    "height": int(height),
                }
            )

        if output_path is not None:

            output_path = Path(
                output_path
            )

            output_path.parent.mkdir(
                parents=True,
                exist_ok=True
            )

            success = cv2.imwrite(
                str(output_path),
                image
            )

            if not success:

                raise RuntimeError(
                    "Unable to save face detection image."
                )

        return detected_faces


face_vision = FaceVision()