"""AidSorter - Automatic Goods Sorting System

This module contains the visualization system.
"""

# we are using 3.9, and most warnings are for 3.10+
# pyright: reportDeprecated=false,reportMissingTypeStubs=false

from dataclasses import dataclass
from typing import Optional

import cv2
from cv2.typing import MatLike
from tflite_support.task.processor import DetectionResult

from aidsorter.logger import LoggerFactory


@dataclass
class StatsStyle:
    """The style for the statistics display.

    Attributes:
        row_size: The height of each row in pixels.
        left_margin: The left margin in pixels.
        text_color: The text color in BGR format.
        font_size: The font size.
        font_thickness: The font thickness.
    """

    row_size: int = 20  # pixels
    left_margin: int = 24  # pixels
    text_color: tuple[int, int, int] = (255, 255, 255)
    font_size: int = 1
    font_thickness: int = 1


def draw_detection_result(
    image: MatLike,
    detection_result: DetectionResult,
    stats_style: Optional[StatsStyle] = None,
) -> MatLike:
    """Draws bounding boxes on the input image and return it.

    Args:
      image: The input RGB image.
      detection_result: The list of all "Detection" entities to be visualize.
      stats_style: The style to use for drawing statistics.

    Returns:
      Image with bounding boxes.
    """

    logger = LoggerFactory().get_logger(__name__)
    stats_style = stats_style or StatsStyle()

    for idx, detection in enumerate(detection_result.detections):
        logger.debug("Creating bounding box for detection #%d", idx)

        # Draw bounding_box
        bbox = detection.bounding_box
        start_point = bbox.origin_x, bbox.origin_y
        end_point = bbox.origin_x + bbox.width, bbox.origin_y + bbox.height
        _ = cv2.rectangle(image, start_point, end_point, stats_style.text_color, 3)

        # Draw label and score
        category = detection.categories[0]
        category_name = category.category_name
        probability = round(category.score, 2)
        result_text = category_name + " (" + str(probability) + ")"
        text_location = (
            stats_style.left_margin + bbox.origin_x,
            stats_style.left_margin + stats_style.row_size + bbox.origin_y,
        )
        _ = cv2.putText(
            image,
            result_text,
            text_location,
            cv2.FONT_HERSHEY_PLAIN,
            stats_style.font_size,
            stats_style.text_color,
            stats_style.font_thickness,
        )

    return image


def draw_fps(
    image: MatLike,
    fps: float,
    fps_stats: list[Optional[float]],
    stats_style: Optional[StatsStyle] = None,
) -> MatLike:
    """Draw the FPS on the top-left corner of the image.

    Args:
        image: The input image.
        fps: The current FPS.
        fps_stats: The min, max, and avg of the FPS.
        stats_style: The style to use for drawing statistics.

    Returns:
        The image with the FPS drawn on it.
    """

    stats_style = stats_style or StatsStyle()
    logger = LoggerFactory().get_logger(__name__)
    logger.debug("Drawing FPS on the image.")

    # Show the FPS
    fps_text = f"FPS = {fps:.1f}"
    fps_min_text = f"MIN = {round(fps_stats[0], 1) if fps_stats[0] else 0}"
    fps_max_text = f"MAX = {round(fps_stats[1], 1) if fps_stats[1] else 0}"
    fps_text_location = (stats_style.left_margin, stats_style.row_size)
    fps_min_text_location = (stats_style.left_margin, stats_style.row_size * 2)
    fps_max_text_location = (stats_style.left_margin, stats_style.row_size * 3)
    _ = cv2.putText(
        image,
        fps_text,
        fps_text_location,
        cv2.FONT_HERSHEY_PLAIN,
        stats_style.font_size,
        stats_style.text_color,
        stats_style.font_thickness,
    )
    _ = cv2.putText(
        image,
        fps_min_text,
        fps_min_text_location,
        cv2.FONT_HERSHEY_PLAIN,
        stats_style.font_size,
        stats_style.text_color,
        stats_style.font_thickness,
    )
    _ = cv2.putText(
        image,
        fps_max_text,
        fps_max_text_location,
        cv2.FONT_HERSHEY_PLAIN,
        stats_style.font_size,
        stats_style.text_color,
        stats_style.font_thickness,
    )

    return image
