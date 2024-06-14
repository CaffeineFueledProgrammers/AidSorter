"""AidSorter - Automatic Goods Sorting System
"""

import logging
import os

NAME = "AidSorter"
VERSION = (0, 1, 0)
TITLE = f"{NAME} v{'.'.join(map(str, VERSION))}"

DEBUG_MODE = (
    logging.DEBUG
    if os.getenv("AIDSORTER_DEBUG", "false") in {"true", "1", "yes", "on"}
    else logging.INFO
)
LOG_FILEPATH = "aidsorter.log"
LOG_FORMAT = "%(asctime)s:%(name)s:%(levelname)s:%(message)s"
LOG_DATE_FORMAT = "%d-%m-%y_%H-%M-%S"
ENCODING = "utf-8"
