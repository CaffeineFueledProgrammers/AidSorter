"""AidSorter - Automatic Goods Sorting System
"""

import logging
import os

NAME = "AidSorter"
VERSION = (0, 2, 0)
TITLE = f"{NAME} v{'.'.join(map(str, VERSION))}"

DEBUG_MODE = (
    logging.DEBUG
    if os.getenv("AIDSORTER_DEBUG", "false") in {"true", "1", "yes", "on"}
    else logging.INFO
)
LOG_FILEPATH = "logs/aidsorter-{0}.log"  # A placeholder for the log file path
LOG_FORMAT = "%(asctime)s:%(name)s:%(levelname)s:%(message)s"
LOG_DATE_FORMAT = "%d-%m-%y_%H-%M-%S"
LOG_MAX_BYTES = 1024 * 1024 * 10  # 10MB
LOG_BACKUP_COUNT = 5  # keep 5 logfiles
ENCODING = "utf-8"

DEFAULT_CONFIG_PATH = os.path.join(os.getcwd(), "aidsorter.conf")
