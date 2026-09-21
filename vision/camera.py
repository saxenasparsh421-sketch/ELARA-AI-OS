"""
ELARA Camera Vision
Local webcam capture and live face detection support.
"""

from pathlib import Path
from datetime import datetime

import cv2


class Camera:

    def __init__(
        self,
        camera_index=0,
        save_dir="data/camera"
    ):

        self.camera_index = camera_index

        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.camera = None

    # =====================================================
    # OPEN CAMERA
    # =====================================================

    def open(self):

        if self.camera is not None:
            return True

        self.camera = cv2.VideoCapture(
            self.camera_index
        )

        if not self.camera.isOpened():

            self.camera.release()
            self.camera = None

            raise RuntimeError(
                "Unable to open the camera."
            )

        return True

    # =====================================================
    # CAPTURE FRAME
    # =====================================================

    def capture(self):

        self.open()

        success, frame = (
            self.camera.read()
        )

        if not success:

            raise RuntimeError(
                "Unable to capture a frame from the camera."
            )

        return frame

    # =====================================================
    # SAVE FRAME
    # =====================================================

    def capture_and_save(self):

        frame = self.capture()

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        image_path = (
            self.save_dir
            / f"camera_{timestamp}.jpg"
        )

        success = cv2.imwrite(
            str(image_path),
            frame
        )

        if not success:

            raise RuntimeError(
                "Unable to save the camera image."
            )

        return image_path

    # =====================================================
    # LIVE CAMERA
    # =====================================================

    def live(self, detector=None):

        self.open()

        print()
        print("[ELARA CAMERA] Live camera started.")
        print("[ELARA CAMERA] Press Q to close.")
        print()

        while True:

            success, frame = (
                self.camera.read()
            )

            if not success:

                print(
                    "[ELARA CAMERA] "
                    "Unable to read camera frame."
                )

                break

            if detector is not None:

                faces = detector.detect_frame(
                    frame
                )

                for face in faces:

                    x = face["x"]
                    y = face["y"]
                    width = face["width"]
                    height = face["height"]

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + width, y + height),
                        (0, 255, 0),
                        2
                    )

            cv2.imshow(
                "ELARA Camera",
                frame
            )

            key = cv2.waitKey(1) & 0xFF

            if key == ord("q"):

                break

        cv2.destroyWindow(
            "ELARA Camera"
        )

        self.close()

    # =====================================================
    # CLOSE CAMERA
    # =====================================================

    def close(self):

        if self.camera is not None:

            self.camera.release()

            self.camera = None


camera = Camera()