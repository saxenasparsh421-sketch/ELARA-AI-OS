from pathlib import Path
from datetime import datetime

from PIL import ImageGrab


class ScreenCapture:
    """Capture the current desktop screen."""

    def __init__(self, save_dir="data/screenshots"):
        self.save_dir = Path(save_dir)
        self.save_dir.mkdir(parents=True, exist_ok=True)

    def capture(self):
        """
        Capture the current screen.

        Returns:
            Path: Path to the saved screenshot.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = self.save_dir / f"screen_{timestamp}.png"

        image = ImageGrab.grab()
        image.save(screenshot_path)

        return screenshot_path

    def capture_image(self):
        """
        Capture the current screen without saving it.

        Returns:
            PIL.Image.Image: Screenshot image.
        """
        return ImageGrab.grab()


screen_capture = ScreenCapture()