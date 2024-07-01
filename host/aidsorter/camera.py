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
from aidsorter.mcu import MCU


class FPSConfig:
    """A helper class to easily process FPS values."""

    def __init__(self, history_len: int = 1000, avg_frame_count: int = 10) -> None:
        """Create a new FPSConfig object.

        Args:
            history_len: The length of the FPS history.
            avg_frame_count: Get the average of the last <avg_frame_count> frames.
        """

        self.frame_count: int = 0  # The current frame count
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.latest_fps: float = 0.0  # The latest FPS value
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


class MCUConfig:
    """A helper class to easily process the MCU configuration file."""

    def __init__(self, config_path: str) -> None:
        """Create a new MCUConfig object.

        Args:
            config_path: The path of the configuration file.
        """

        self.__logger = LoggerFactory().get_logger(__name__)
        self.__config_path = config_path
        self.__logger.info("Reading configuration file: %s", config_path)
        with open(config_path, "r", encoding="utf-8") as config_file:
            contents = config_file.readlines()

        # These are the default values so it's fine to redeclare them.
        self.resolution: tuple[int, int] = (  # pyright: ignore[reportRedeclaration]
            640,
            480,
        )
        bucket1_contents: tuple[str, ...] = ()  # pyright: ignore[reportRedeclaration]
        bucket2_contents: tuple[str, ...] = ()  # pyright: ignore[reportRedeclaration]
        bucket3_contents: tuple[str, ...] = ()  # pyright: ignore[reportRedeclaration]
        bucket4_contents: tuple[str, ...] = ()  # pyright: ignore[reportRedeclaration]

        for line in contents:
            self.__logger.debug("Processing line: %s", line.replace("\n", "\\n"))
            if line.startswith("#") or line.strip() == "":
                # self.__logger.debug("Skipping line...")
                continue  # Skip comments and empty lines

            key, _, value = line.strip().partition("=")
            if key == "cpu_threads":
                self.__cpu_threads = int(value)
                if self.__cpu_threads < 1:
                    self.__cpu_threads = multiprocessing.cpu_count()

            elif key == "resolution":
                self.resolution: tuple[int, int] = (
                    int(value.partition("x")[0]),
                    int(value.partition("x")[2]),
                )

            elif key == "baudrate":
                self.__baudrate = int(value)

            elif key == "mcu_connection_timeout":
                self.mcu_connection_timeout: float = float(value)

            elif key == "bucket1_contents":
                bucket1_contents: tuple[str, ...] = (
                    tuple(value.split(",")) if len(value) > 0 else ()
                )

            elif key == "bucket2_contents":
                bucket2_contents: tuple[str, ...] = (
                    tuple(value.split(",")) if len(value) > 0 else ()
                )

            elif key == "bucket3_contents":
                bucket3_contents: tuple[str, ...] = (
                    tuple(value.split(",")) if len(value) > 0 else ()
                )

            elif key == "bucket4_contents":
                bucket4_contents: tuple[str, ...] = (
                    tuple(value.split(",")) if len(value) > 0 else ()
                )

            else:
                raise exceptions.InvalidMCUConfigError(f"Unknown config key: {key}")

        self.bucket_contents: tuple[
            tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]
        ] = (
            bucket1_contents,
            bucket2_contents,
            bucket3_contents,
            bucket4_contents,
        )

        self.__logger.info("Configuration loaded successfully.")
        self.__logger.info("\tCPU Threads: %s", self.cpu_threads)
        self.__logger.info("\tResolution: %s", self.resolution)
        self.__logger.info("\tBaudrate: %s", self.baudrate)
        self.__logger.info("\tBucket 1 has %s item/s", len(self.bucket_contents[0]))
        self.__logger.info("\tBucket 2 has %s item/s", len(self.bucket_contents[1]))
        self.__logger.info("\tBucket 3 has %s item/s", len(self.bucket_contents[2]))
        self.__logger.info("\tBucket 4 has %s item/s", len(self.bucket_contents[3]))

        self.__logger.debug("\tBucket 1 contents: %s", self.bucket_contents[0])
        self.__logger.debug("\tBucket 2 contents: %s", self.bucket_contents[1])
        self.__logger.debug("\tBucket 3 contents: %s", self.bucket_contents[2])
        self.__logger.debug("\tBucket 4 contents: %s", self.bucket_contents[3])

    @property
    def config_path(self) -> str:
        """Get the path of the configuration file.

        Returns:
            The path of the configuration file.
        """

        return self.__config_path

    @property
    def baudrate(self) -> int:
        """Get the baudrate of the MCU.
        Returns:
            The baudrate of the MCU.
        """

        return self.__baudrate

    @property
    def cpu_threads(self) -> int:
        """Get the number of CPU threads to use.

        Returns:
            The number of CPU threads to use.
        """

        return self.__cpu_threads


def capture(
    config_path: str,
    camera_id: int = 1,
    *,
    mcu_port: str = "/dev/ttyUSB0",
    model_name: str = "default.tflite",
    camera_feed: bool = True,
) -> int:
    """Capture video from the camera and detect objects.

    Args:
        config_path: The path of the configuration file.
        camera_id: The ID of the camera to use. (default: 0)
        mcu_port: The port of the MCU. (default: "/dev/ttyUSB0")
        model_name: The name of the model to use. (default: "default.tflite")
        camera_feed: Display the camera feed. (default: True)

    Raises:
        exceptions.CameraError: Raised when the camera is not available.

    Returns:
        The exit code.
    """

    fps = FPSConfig()
    config = MCUConfig(config_path)
    stats_style = visualizer.StatsStyle()
    tf_detector = detector.create_detector(model_name, config.cpu_threads)
    mcu = MCU(mcu_port, config.baudrate, config.mcu_connection_timeout)

    logger = LoggerFactory().get_logger(__name__)
    logger.info("Starting the detection process...")
    logger.info("Using camera ID: %s", camera_id)
    logger.info(
        "Using camera resolution: %sx%s", config.resolution[0], config.resolution[1]
    )
    logger.info("Using CPU threads: %s", config.cpu_threads)
    cam_cap = cv2.VideoCapture(camera_id)
    logger.info("Backend API name: %s", cam_cap.getBackendName())
    if not cam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.resolution[0]):
        raise exceptions.CameraError("Unable to set the camera width.")

    if not cam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.resolution[1]):
        raise exceptions.CameraError("Unable to set the camera height.")

    logger.info("Starting camera loop...")
    fps.start_time = time.time()  # Start the timer
    while cam_cap.isOpened():
        try:
            read_success, image = cam_cap.read()
            if not read_success:
                logger.error("Unable to read data from webcam.")
                raise exceptions.CameraError("ERROR: Unable to read data from webcam.")

            fps.frame_count += 1
            image = cv2.flip(image, 1)

            # Detect objects in the image
            detection_result = detector.detect_objects(tf_detector, image)
            logger.info("Detected objects: %d", len(detection_result.detections))
            # logger.debug("Raw Detection: %s", detection_result.detections)
            logger.debug(
                "Detection: %s",
                [
                    ",".join([dc.category_name for dc in detection.categories])
                    for detection in detection_result.detections
                ],
            )

            if len(detection_result.detections) > 1:
                # TODO: enable red LED light instead
                logger.error(
                    "%s object/s detected. Will not proceed.",
                    len(detection_result.detections),
                )

            elif len(detection_result.detections) == 1:
                # TODO: Tell MCU to open the specified gate.
                object_category: str = (
                    detection_result.detections[0].categories[0].category_name
                )
                if object_category in config.bucket_contents[0]:
                    logger.info("Object %s belongs to Bucket 1.", object_category)
                    mcu.put_object(1)

                elif object_category in config.bucket_contents[1]:
                    logger.info("Object %s belongs to Bucket 2.", object_category)
                    mcu.put_object(2)

                elif object_category in config.bucket_contents[2]:
                    logger.info("Object %s belongs to Bucket 3.", object_category)
                    mcu.put_object(3)

                elif object_category in config.bucket_contents[3]:
                    logger.info("Object %s belongs to Bucket 4.", object_category)
                    mcu.put_object(4)

                else:
                    logger.warning("Unknown object category: %s", object_category)
                    logger.warning("Object will be put in Bucket 5.")
                    mcu.put_object(5)

            # Calculate the FPS
            if fps.frame_count % fps.avg_frame_count == 0:
                fps.end_time = time.time()
                fps.latest_fps = fps.avg_frame_count / (fps.end_time - fps.start_time)
                fps.start_time = time.time()
                logger.debug("FPS = %s", fps.latest_fps)
                fps.add_record(fps.latest_fps)

            if camera_feed:
                # draw detection results,
                # draw FPS stats,
                # and display the camera feed.
                cv2.imshow(
                    f"{info.TITLE} | Camera Feed",
                    visualizer.draw_fps(
                        visualizer.draw_detection_result(
                            image, detection_result, stats_style
                        ),
                        fps.latest_fps,
                        (fps.minimum, fps.maximum, fps.average),
                        stats_style,
                    ),
                )

                # Stop the program if the ESC key is pressed.
                if cv2.waitKey(1) == 27:
                    logger.info("ESC key pressed. Exiting...")
                    break

        except KeyboardInterrupt:
            logger.info("KeyboardInterrupt detected.")
            break

    logger.info("Releasing camera...")
    cam_cap.release()
    logger.info("Destroying all windows...")
    cv2.destroyAllWindows()
    logger.info("Done.")
    logger.info("Min FPS: %s", fps.minimum)
    logger.info("Max FPS: %s", fps.maximum)
    logger.info("Avg FPS: %s", fps.average)

    return 0
