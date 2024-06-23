"""AidSorter - Automatic Goods Sorting System

This module contains the main function of the program.
"""

# quit your whining
# pyright: reportDeprecated=false

import argparse
import os
import sys
from typing import Optional

from cv2.version import opencv_version

from aidsorter import camera, info
from aidsorter.logger import LoggerFactory


def main() -> int:
    """The main function of the program.

    Returns:
        The exit code of the program.
    """

    arg_parser = argparse.ArgumentParser(info.TITLE)

    _ = arg_parser.add_argument(
        "-c", "--camera", type=int, default=1, help="The index of the camera to use."
    )
    _ = arg_parser.add_argument(
        "-x", "--width", type=int, default=640, help="The width of the camera frame."
    )
    _ = arg_parser.add_argument(
        "-y", "--height", type=int, default=480, help="The height of the camera frame."
    )
    _ = arg_parser.add_argument(
        "-t",
        "--threads",
        type=int,
        default=None,
        help="The number of threads to use. (default: CPU count)",
    )
    _ = arg_parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="default.tflite",
        help='Override the model to use. Should be located in the "models/" directory.',
    )

    parsed_args = arg_parser.parse_args()
    # ignore galore!
    camera_id: int = parsed_args.camera  # pyright: ignore[reportAny]
    cam_width: int = parsed_args.width  # pyright: ignore[reportAny]
    cam_height: int = parsed_args.height  # pyright: ignore[reportAny]
    cpu_threads: Optional[int] = parsed_args.threads  # pyright: ignore[reportAny]
    model_name: str = parsed_args.model  # pyright: ignore[reportAny]

    logger = LoggerFactory().get_logger(__name__)
    logger.info("%s started.", info.TITLE)
    logger.info("Environment:")
    logger.debug("\tCMD: %s", str(sys.argv))
    logger.info("\tPython version: %s", sys.version)
    logger.info("\tOpenCV version: %s", opencv_version)
    logger.info("\tPWD: %s", os.getcwd())
    logger.info("\tCamera ID: %d", camera_id)
    logger.info("\tModel Name: %s", model_name)
    logger.info("\tDebug mode: %s", "Enabled" if info.DEBUG_MODE else "Disabled")

    exit_code = camera.capture(
        camera_id,
        resolution=(cam_width, cam_height),
        cpu_threads=cpu_threads,
        model_name=model_name,
    )

    logger.info("%s exited with code %s.", info.TITLE, exit_code)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
