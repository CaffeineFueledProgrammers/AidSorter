"""AidSorter - Automatic Goods Sorting System
"""

import argparse
import sys

from cv2 import __version__ as cv2_version

from aidsorter import camera, info
from aidsorter.logger import LoggerFactory


def main() -> int:
    """The main function of the program.

    Returns:
        The exit code of the program.
    """

    arg_parser = argparse.ArgumentParser(info.TITLE)

    _ = arg_parser.add_argument(
        "-c", "--camera", type=int, default=0, help="The index of the camera to use."
    )

    parsed_args = arg_parser.parse_args()
    camera_id: int = parsed_args.camera  # pyright: ignore[reportAny]

    logger = LoggerFactory().get_logger(__name__)
    logger.info("%s started.", info.TITLE)
    logger.info("Environment:")
    logger.debug("\tCMD: %s", str(sys.argv))
    logger.info("\tPython version: %s", sys.version)
    logger.info("\tOpenCV version: %s", cv2_version)
    logger.info("\tTensorFlow version: N/A")  # FIXME: Add TensorFlow version
    logger.info("\tCamera ID: %d", camera_id)
    logger.info("\tDebug mode: %s", "enabled" if info.DEBUG_MODE else "disabled")

    exit_code = camera.capture(camera_id)

    logger.info("%s exited with code %s.", info.TITLE, exit_code)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
