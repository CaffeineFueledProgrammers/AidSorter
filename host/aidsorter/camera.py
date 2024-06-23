"""AidSorter - Automatic Goods Sorting System

This module contains the image recognition system.
"""

# we are using 3.9, and most warnings are for 3.10+
# pyright: reportDeprecated=false

import time
from typing import Optional

import cv2

from aidsorter import detector, exceptions, info, visualizer
from aidsorter.logger import LoggerFactory


def capture(  # pylint: disable=R0914,R0915
    camera_id: int = 0,
    *,
    width: int = 640,
    height: int = 480,
    cpu_threads: Optional[int] = None,
    model_name: str = "default.tflite",
) -> int:
    """Capture video from the camera and detect objects.

    Args:
        camera_id: The ID of the camera to use. (default: 0)
        width: The width of the camera frame. (default: 640)
        height: The height of the camera frame. (default: 480)
        cpu_threads: Override the number of CPU threads to use.
        model_name: The name of the model to use. (default: "default.tflite")

    Raises:
        exceptions.CameraError: Raised when the camera is not available.

    Returns:
        The exit code.
    """

    frame_counter = 0
    fps = 0
    fps_stats: list[Optional[float]] = [  # min, max, avg of the last 100 fps values
        None,
        None,
        None,
    ]
    last_fps: list[float] = []
    last_fps_hist_len = 1000
    fps_avg_frame_count: int = 10
    stats_style = visualizer.StatsStyle()
    tf_detector = detector.create_detector(model_name, cpu_threads)

    start_time = time.time()
    logger = LoggerFactory().get_logger(__name__)

    logger.info("Starting the detection process...")
    logger.info("Using camera ID: %s", camera_id)
    logger.info("Using camera resolution: %sx%s", width, height)
    logger.info("Using CPU threads: %s", cpu_threads)
    cam_cap = cv2.VideoCapture(camera_id)
    _ = cam_cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    _ = cam_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    while cam_cap.isOpened():
        success, raw_image = cam_cap.read()
        if not success:
            logger.error("Unable to read data from webcam.")
            raise exceptions.CameraError("ERROR: Unable to read data from webcam.")

        frame_counter += 1
        raw_image = cv2.flip(raw_image, 1)

        detection_result = detector.detect_objects(tf_detector, raw_image)
        processed_image = visualizer.draw_detection_result(
            raw_image, detection_result, stats_style
        )

        # Calculate the FPS
        if frame_counter % fps_avg_frame_count == 0:
            end_time = time.time()
            fps = fps_avg_frame_count / (end_time - start_time)
            start_time = time.time()
            logger.debug("FPS = %s", fps)
            # only keep the last <last_fps_hist_len> fps values
            # last_fps.append(fps)
            last_fps = last_fps[-last_fps_hist_len:] + [fps]

            if fps_stats[0] is None or fps < fps_stats[0]:
                fps_stats[0] = fps

            if fps_stats[1] is None or fps > fps_stats[1]:
                fps_stats[1] = fps

        processed_image = visualizer.draw_fps(
            processed_image, fps, fps_stats, stats_style
        )

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
            logger.info("ESC key pressed. Exiting...")
            break

        cv2.imshow(info.TITLE, processed_image)

    logger.info("Releasing camera...")
    cam_cap.release()
    logger.info("Destroying all windows...")
    cv2.destroyAllWindows()
    logger.info("Done.")
    try:
        logger.info("Min FPS: %s", fps_stats[0])
        logger.info("Max FPS: %s", fps_stats[1])
        logger.info("Avg FPS: %s", sum(last_fps) / len(last_fps))

    except ZeroDivisionError:
        logger.warning("Unable to calculate the average FPS.")

    return 0
