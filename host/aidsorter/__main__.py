"""AidSorter - Automatic Goods Sorting System
"""

import sys

from aidsorter import info
from aidsorter.logger import LoggerFactory


def main() -> int:
    """The main function of the program.

    Returns:
        The exit code of the program.
    """

    logger = LoggerFactory().get_logger(__name__)
    logger.info(info.TITLE)

    return 0


if __name__ == "__main__":
    sys.exit(main())
