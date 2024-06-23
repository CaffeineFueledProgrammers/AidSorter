"""AidSorter - Automatic Goods Sorting System
"""

# we are using 3.9, and most warnings are for 3.10+
# pyright: reportDeprecated=false

import logging
from typing import Optional

from aidsorter import info


class LoggerFactory:  # pylint: disable=R0903,C0115
    def __init__(
        self,
        log_level: Optional[int] = None,
    ):
        """Create a new LoggerFactory object.

        Args:
            log_level: Override the log level with the provided value.
        """

        # Set the log level based on the environment variable, or
        # the provided log level.
        self.log_level = log_level if log_level is not None else (info.DEBUG_MODE)

    def get_logger(self, name: str) -> logging.Logger:
        """Get a logger with the provided name.

        Args:
            name: The name of the logger.

        Returns:
            The logger object.
        """

        logger = logging.getLogger(name)
        logger.setLevel(self.log_level)

        # Add a handler if one does not already exist.
        if not logger.handlers:
            # handlers
            stream_handler = logging.StreamHandler()
            file_handler = logging.FileHandler(
                info.LOG_FILEPATH, encoding=info.ENCODING
            )

            # formatters
            formatter = logging.Formatter(
                fmt=info.LOG_FORMAT,
                datefmt=info.LOG_DATE_FORMAT,
            )

            # add formatters to handlers
            stream_handler.setFormatter(formatter)
            file_handler.setFormatter(formatter)

            # add handlers to logger
            logger.addHandler(stream_handler)
            logger.addHandler(file_handler)

        return logger
