"""AidSorter - Automatic Goods Sorting System

This module contains the image recognition system.
"""

import time

import cv2

from aidsorter import exceptions, info
from aidsorter.logger import LoggerFactory


def capture(  # pylint: disable=R0914
    camera_id: int = 0, width: int = 640, height: int = 480
) -> int:
    """Capture video from the camera and detect objects.

    Args:
        camera_id: The ID of the camera to use. (default: 0)
    """

    frame_counter = 0
    fps = 0

    row_size = 20  # pixels
    left_margin = 24  # pixels
    text_color = (255, 255, 255)
    font_size = 1
    font_thickness = 1
    fps_avg_frame_count = 10

    start_time = time.time()
    logger = LoggerFactory().get_logger(__name__)

    logger.info("Starting the detection process...")
    logger.info("Using camera ID: %s", camera_id)
    logger.info("Using camera resolution: %sx%s", width, height)
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

        # Convert the image from BGR to RGB as required by the TFLite model.
        # Create a TensorImage object from the RGB image.
        # Run object detection estimation using the model.
        # Draw keypoints and edges on input image

        # Calculate the FPS
        if frame_counter % fps_avg_frame_count == 0:
            end_time = time.time()
            fps = fps_avg_frame_count / (end_time - start_time)
            start_time = time.time()
            logger.debug("FPS = %s", fps)

        # Show the FPS
        fps_text = f"FPS = {fps:.1f}"
        text_location = (left_margin, row_size)
        _ = cv2.putText(
            raw_image,
            fps_text,
            text_location,
            cv2.FONT_HERSHEY_PLAIN,
            font_size,
            text_color,
            font_thickness,
        )

        # Stop the program if the ESC key is pressed.
        if cv2.waitKey(1) == 27:
            logger.info("ESC key pressed. Exiting...")
            break

        cv2.imshow(info.TITLE, raw_image)

    logger.info("Releasing camera...")
    cam_cap.release()
    logger.info("Destroying all windows...")
    cv2.destroyAllWindows()
    logger.info("Done.")
    return 0
