"""AidSorter - Automatic Goods Sorting System

This module contains the main function of the program.
"""

import os
import sys

from aidsorter import info, detector
from aidsorter.logger import LoggerFactory
from cv2.version import opencv_version
from flask import Flask, request
import multiprocessing
import base64
from cv2.typing import MatLike

app = Flask(__name__)

deez = detector.create_detector("models/default.tflite", multiprocessing.cpu_count())


@app.route("/", methods=["POST"])
def detect():
    img = base64.b64decode(request.data["frame"].encode())
    detection_result = detector.detect_objects(deez, img)
    return ",".join(
        [dc.category_name for dc in detection_result.detections[0].categories]
    )


def main():
    """The main function of the program."""

    logger = LoggerFactory().get_logger(__name__)
    logger.info("%s started.", info.TITLE)
    logger.info("Environment:")
    logger.debug("\tCMD: %s", str(sys.argv))
    logger.info("\tPython version: %s", sys.version)
    logger.info("\tOpenCV version: %s", opencv_version)
    logger.info("\tPWD: %s", os.getcwd())

    app.run("0.0.0.0", 5000)


if __name__ == "__main__":
    main()
