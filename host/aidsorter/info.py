"""AidSorter - Automatic Goods Sorting System
"""

NAME = "AidSorter"
VERSION = (0, 1, 0)
TITLE = f"{NAME} v{'.'.join(map(str, VERSION))}"

LOG_FILEPATH = "aidsorter.log"
LOG_FORMAT = "%(asctime)s:%(name)s:%(levelname)s:%(message)s"
LOG_DATE_FORMAT = "%d-%m-%y_%H-%M-%S"
ENCODING = "utf-8"
