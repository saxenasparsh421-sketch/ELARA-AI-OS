"""
ELARA Local Face Memory
-----------------------
Learns and recognizes Boss locally.

Storage:
    data/face/elara_face.yml
    data/face/samples/
"""

from pathlib import Path
import time

import cv2


class FaceMemory:

    def __init__(self):
        self.project_root = Path(__file__).resolve().parents[1]

        self.face_dir = (
            self.project_root
            / "data"
            / "face"
        )

        self.samples_dir = (
            self.face_dir
            / "samples"
        )

        self.model_path = (
            self.face_dir
            / "elara_face.yml"
        )

        self.cascade_path = (
            self.project_root
            / "data"
            / "models"
            / "haarcascade_frontalface_default.xml"
        )

        self.face_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.samples_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.recognizer = None

        try:
            self.recognizer = (
                cv2.face.LBPHFaceRecognizer_create()
            )
        except AttributeError:
            self.recognizer = None

    # ---------------------------------------------------------
    # CASCADE
    # ---------------------------------------------------------

    def _load_cascade(self):

        if self.cascade_path.exists():
            cascade = cv2.CascadeClassifier(
                str(self.cascade_path)
            )

            if not cascade.empty():
                return cascade

        fallback = (
            Path(cv2.data.haarcascades)
            / "haarcascade_frontalface_default.xml"
        )

        cascade = cv2.CascadeClassifier(
            str(fallback)
        )

        if cascade.empty():
            raise RuntimeError(
                "Face detection model could not be loaded."
            )

        return cascade

    # ---------------------------------------------------------
    # CAMERA
    # ---------------------------------------------------------

    def _open_camera(self):

        camera = cv2.VideoCapture(0)

        if not camera.isOpened():
            raise RuntimeError(
                "Camera could not be opened."
            )

        return camera

    # ---------------------------------------------------------
    # REMEMBER FACE
    # ---------------------------------------------------------

    def remember_face(
        self,
        samples_needed=30
    ):

        if self.recognizer is None:
            return (
                "Face recognition module is missing. "
                "Install opencv-contrib-python first, Boss."
            )

        cascade = self._load_cascade()

        camera = self._open_camera()

        saved_files = []

        frame_count = 0

        print(
            "[FACE] Learning Boss face..."
        )

        try:

            while len(saved_files) < samples_needed:

                success, frame = camera.read()

                if not success:
                    continue

                frame_count += 1

                gray = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY
                )

                faces = cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(100, 100)
                )

                if len(faces) == 0:
                    cv2.imshow(
                        "ELARA - Remember Face",
                        frame
                    )

                    if (
                        cv2.waitKey(1)
                        & 0xFF
                    ) == 27:
                        return (
                            "Face learning cancelled, Boss."
                        )

                    continue

                x, y, w, h = max(
                    faces,
                    key=lambda item:
                    item[2] * item[3]
                )

                cv2.rectangle(
                    frame,
                    (x, y),
                    (x + w, y + h),
                    (0, 255, 0),
                    2
                )

                cv2.putText(
                    frame,
                    f"Learning {len(saved_files)}/{samples_needed}",
                    (x, max(25, y - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (0, 255, 0),
                    2
                )

                cv2.imshow(
                    "ELARA - Remember Face",
                    frame
                )

                # Capture every few frames
                if frame_count % 5 == 0:

                    face = gray[
                        y:y + h,
                        x:x + w
                    ]

                    if (
                        face.size == 0
                    ):
                        continue

                    face = cv2.resize(
                        face,
                        (200, 200)
                    )

                    filename = (
                        self.samples_dir
                        / f"boss_{len(saved_files):03d}.jpg"
                    )

                    cv2.imwrite(
                        str(filename),
                        face
                    )

                    saved_files.append(
                        filename
                    )

                if (
                    cv2.waitKey(1)
                    & 0xFF
                ) == 27:

                    return (
                        "Face learning cancelled, Boss."
                    )

            print(
                "[FACE] Samples captured:",
                len(saved_files)
            )

        finally:

            camera.release()
            cv2.destroyAllWindows()

        # -----------------------------------------------------
        # TRAIN
        # -----------------------------------------------------

        images = []
        labels = []

        for file in saved_files:

            image = cv2.imread(
                str(file),
                cv2.IMREAD_GRAYSCALE
            )

            if image is None:
                continue

            images.append(image)
            labels.append(1)

        if not images:
            return (
                "I couldn't collect usable face samples, Boss."
            )

        self.recognizer.train(
            images,
            # OpenCV expects integer labels
            # and ours is always 1 = Boss.
            cv2.UMat(
                __import__("numpy").array(
                    labels,
                    dtype="int32"
                )
            )
        )

        self.recognizer.write(
            str(self.model_path)
        )

        print(
            "[FACE] Face memory saved:"
        )

        print(
            self.model_path
        )

        return (
            "Done Boss. I have learned your face "
            "and saved the face memory locally."
        )

    # ---------------------------------------------------------
    # LOAD MODEL
    # ---------------------------------------------------------

    def _load_model(self):

        if self.recognizer is None:
            return False

        if not self.model_path.exists():
            return False

        self.recognizer.read(
            str(self.model_path)
        )

        return True

    # ---------------------------------------------------------
    # RECOGNIZE FACE
    # ---------------------------------------------------------

    def recognize(
        self,
        timeout=8,
        threshold=70.0
    ):

        if not self._load_model():

            return (
                "I haven't learned your face yet, Boss. "
                "Say 'remember me' first."
            )

        cascade = self._load_cascade()
        camera = self._open_camera()

        start = time.time()

        matches = 0

        try:

            while (
                time.time() - start
            ) < timeout:

                success, frame = camera.read()

                if not success:
                    continue

                gray = cv2.cvtColor(
                    frame,
                    cv2.COLOR_BGR2GRAY
                )

                faces = cascade.detectMultiScale(
                    gray,
                    scaleFactor=1.2,
                    minNeighbors=5,
                    minSize=(100, 100)
                )

                for x, y, w, h in faces:

                    face = gray[
                        y:y + h,
                        x:x + w
                    ]

                    face = cv2.resize(
                        face,
                        (200, 200)
                    )

                    label, distance = (
                        self.recognizer.predict(
                            face
                        )
                    )

                    if (
                        label == 1
                        and distance <= threshold
                    ):

                        matches += 1

                        text = "BOSS"

                    else:

                        text = "UNKNOWN"

                    cv2.rectangle(
                        frame,
                        (x, y),
                        (x + w, y + h),
                        (0, 255, 0)
                        if text == "BOSS"
                        else (0, 0, 255),
                        2
                    )

                    cv2.putText(
                        frame,
                        text,
                        (x, max(25, y - 10)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.8,
                        (0, 255, 0)
                        if text == "BOSS"
                        else (0, 0, 255),
                        2
                    )

                cv2.imshow(
                    "ELARA - Face Scan",
                    frame
                )

                if (
                    cv2.waitKey(1)
                    & 0xFF
                ) == 27:

                    return (
                        "Face scan cancelled, Boss."
                    )

                if matches >= 3:

                    return (
                        "Welcome back Boss. "
                        "I recognize you."
                    )

        finally:

            camera.release()
            cv2.destroyAllWindows()

        return (
            "I couldn't confidently recognize you, Boss."
        )

    # ---------------------------------------------------------
    # STATUS
    # ---------------------------------------------------------

    def is_ready(self):

        return (
            self.recognizer is not None
            and self.model_path.exists()
        )