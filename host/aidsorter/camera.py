"""AidSorter - Automatic Goods Sorting System

This module contains the system that handles camera features.
"""

# quit your whining
# pyright: reportDeprecated=false

import multiprocessing
import time
from typing import Optional

import cv2

from aidsorter import detector, exceptions, info, visualizer
from aidsorter.logger import LoggerFactory


class FPSConfig:
    """A helper class to easily process FPS values."""

    def __init__(self, history_len: int = 1000, avg_frame_count: int = 10) -> None:
        """Create a new FPSConfig object.

        Args:
            history_len: The length of the FPS history.
            avg_frame_count: Get the average of the last <avg_frame_count> frames.
        """

        self.frame_count = 0  # The current frame count
        self.latest_fps = 0  # The latest FPS value
        self.__fps: list[float] = []
        self.__history_len = history_len
        self.__avg_frame_count: int = avg_frame_count

    @property
    def history(self) -> list[float]:
        """Get the FPS history.

        Returns:
            The FPS history.
        """

        return self.__fps

    @property
    def history_len(self) -> int:
        """Get the length limit of the FPS history.

        Returns:
            The length limit of the FPS history.
        """

        return self.__history_len

    @property
    def avg_frame_count(self) -> int:
        """Get the frame count for the average FPS.

        Returns:
            The frame count for the average FPS.
        """

        return self.__avg_frame_count

    @property
    def minimum(self) -> Optional[float]:
        """Get the minimum FPS value.

        Returns:
            The minimum FPS value.
        """

        return min(self.__fps) if self.__fps else None

    @property
    def maximum(self) -> Optional[float]:
        """Get the maximum FPS value.

        Returns:
            The maximum FPS value.
        """

        return max(self.__fps) if self.__fps else None

    @property
    def average(self) -> Optional[float]:
        """Get the average FPS value.

        Returns:
            The average FPS value.
        """

        return sum(self.__fps) / len(self.__fps) if self.__fps else None

    def add_record(self, fps: float) -> None:
        """Add a new FPS record to the history.

        Args:
            fps: The FPS value to add.
        """

        self.__fps = self.__fps[-self.__history_len :] + [fps]


def capture(
    camera_id: int = 1,
    *,
    resolution: tuple[int, int] = (640, 480),
    cpu_threads: Optional[int] = None,
    model_name: str = "default.tflite",
) -> int:
    """Capture video from the camera and detect objects.

    Args:
        camera_id: The ID of the camera to use. (default: 0)
        resolution: The resolution of the camera frame. (default: (640, 480))
        cpu_threads: Override the number of CPU threads to use.
        model_name: The name of the model to use. (default: "default.tflite")

    Raises:
        exceptions.CameraError: Raised when the camera is not available.

    Returns:
        The exit code.
    """

    fps = FPSConfig()
    stats_style = visualizer.StatsStyle()
    cpu_threads = cpu_threads or multiprocessing.cpu_count()
    tf_detector = detector.create_detector(model_name, cpu_threads)

    start_time = time.time()
    logger = LoggerFactory().get_logger(__name__)

    logger.info("Starting the detection process...")
    logger.info("Using camera ID: %s", camera_id)
    logger.info("Using camera resolution: %sx%s", resolution[0], resolution[1])
    logger.info("Using CPU threads: %s", cpu_threads)
    cam_cap = cv2.VideoCapture(camera_id)
    _ = cam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    _ = cam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])

    while cam_cap.isOpened():
        read_success, image = cam_cap.read()
        if not read_success:
            logger.error("Unable to read data from webcam.")
            raise exceptions.CameraError("ERROR: Unable to read data from webcam.")

        fps.frame_count += 1
        image = cv2.flip(image, 1)

        detection_result = detector.detect_objects(tf_detector, image)
        image = visualizer.draw_detection_result(image, detection_result, stats_style)

        # Calculate the FPS
        if fps.frame_count % fps.avg_frame_count == 0:
            end_time = time.time()
            latest_fps = fps.avg_frame_count / (end_time - start_time)
            start_time = time.time()
            logger.debug("FPS = %s", latest_fps)
            fps.add_record(latest_fps)

        image = visualizer.draw_fps(
            image,
            fps.latest_fps,
            (fps.minimum, fps.maximum, fps.average),
            stats_style,
        )

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
            logger.info("ESC key pressed. Exiting...")
            break

        cv2.imshow(info.TITLE, image)

    logger.info("Releasing camera...")
    cam_cap.release()
    logger.info("Destroying all windows...")
    cv2.destroyAllWindows()
    logger.info("Done.")
    logger.info("Min FPS: %s", fps.minimum)
    logger.info("Max FPS: %s", fps.maximum)
    logger.info("Avg FPS: %s", fps.average)

    return 0
