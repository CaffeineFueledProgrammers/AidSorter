"""AidSorter - Automatic Goods Sorting System

This module contains the image recognition system.
"""

# quit your whining
# pyright: reportMissingTypeStubs=false

import os

import cv2
from cv2.typing import MatLike
from tflite_support.task import core as tf_core
from tflite_support.task import processor as tf_processor
from tflite_support.task import vision as tf_vision

from aidsorter import exceptions
from aidsorter.logger import LoggerFactory


def create_detector(model_name: str, num_threads: int) -> tf_vision.ObjectDetector:
    """Create a new object detector from the given model name.

    Args:
        model_name: The filename of the model to use located in `models/` directory.
        num_threads: The number of threads to use.

    Returns:
        The new object instance.
    """

    logger = LoggerFactory().get_logger(__name__)

    logger.info("Using %s CPU threads for object detection.", num_threads)
    available_models = os.listdir(os.path.join(os.getcwd(), "models"))
    logger.debug("Files in `models/` directory: %s", str(available_models))
    if model_name not in available_models:
        logger.fatal("Model '%s' not found in available models.", model_name)
        raise exceptions.ModelNotFoundError(
            f"Model '{model_name}' not found in available models."
        )

    logger.info("Model '%s' found in available models.", model_name)
    model = os.path.join(os.getcwd(), "models", model_name)
    logger.debug("Using model `%s`", model)

    return tf_vision.ObjectDetector.create_from_options(
        tf_vision.ObjectDetectorOptions(
            base_options=tf_core.BaseOptions(file_name=model, num_threads=num_threads),
            detection_options=tf_processor.DetectionOptions(
                max_results=3, score_threshold=0.3
            ),
        )
    )


def detect_objects(
    detector: tf_vision.ObjectDetector, image: MatLike
) -> tf_processor.DetectionResult:
    """Detect objects in the given image using the provided detector.

    Args:
        detector: The object detector instance.
        image: The image to process.

    Returns:
        The detection result.
    """

    # Convert the image from BGR to RGB as required by the TFLite model.
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Create a TensorImage object from the RGB image.
    # pylint: disable-next=line-too-long
    input_tensor = tf_vision.TensorImage.create_from_array(rgb_image)  # type: ignore[reportUnknownMemberType]

    # Run object detection estimation using the model.
    return detector.detect(input_tensor)
