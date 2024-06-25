"""AidSorter - Automatic Goods Sorting System

This module contains the main function of the program.
"""

import argparse
import logging
import os
import sys
import traceback

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
        "-C", "--camera", type=int, default=1, help="The index of the camera to use."
    )
    _ = arg_parser.add_argument(
        "-c",
        "--config",
        default=info.DEFAULT_CONFIG_PATH,
        help="The path to the configuration file.",
    )
    _ = arg_parser.add_argument(
        "-m",
        "--model",
        type=str,
        default="default.tflite",
        help='Override the model to use. Should be located in the "models/" directory.',
    )
    _ = arg_parser.add_argument(
        "-d",
        "--display",
        action="store_true",
        help="Display the camera feed.",
    )

    parsed_args = arg_parser.parse_args()
    # ignore galore!
    camera_id: int = parsed_args.camera  # pyright: ignore[reportAny]
    config_path: str = (
        parsed_args.config or info.DEFAULT_CONFIG_PATH  # pyright: ignore[reportAny]
    )
    model_name: str = parsed_args.model  # pyright: ignore[reportAny]
    display: bool = parsed_args.display  # pyright: ignore[reportAny]

    logger = LoggerFactory().get_logger(__name__)
    logger.info("%s started.", info.TITLE)
    logger.info("Environment:")
    logger.debug("\tCMD: %s", str(sys.argv))
    logger.info("\tPython version: %s", sys.version)
    logger.info("\tOpenCV version: %s", opencv_version)
    logger.info("\tPWD: %s", os.getcwd())
    logger.info("\tCamera ID: %d", camera_id)
    logger.info("\tConfig Path: %s", config_path)
    logger.info("\tModel Name: %s", model_name)
    logger.info("\tCamera Feed: %s", "Enabled" if display else "Disabled")
    logger.info(
        "\tDebug mode: %s",
        "Enabled" if info.DEBUG_MODE == logging.DEBUG else "Disabled",
    )

    try:
        exit_code = camera.capture(
            config_path,
            camera_id,
            model_name=model_name,
            camera_feed=display,
        )

    except Exception as e:  # pylint: disable=broad-exception-caught
        logger.fatal("A fatal error occurred: %s", e)
        logger.fatal("\n%s", traceback.format_exc())
        exit_code = 255

    logger.info("%s exited with code %s.", info.TITLE, exit_code)
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
