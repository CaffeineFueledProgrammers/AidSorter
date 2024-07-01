"""AidSorter - Automatic Goods Sorting System

This module contains all custom exceptions
"""


class CameraError(Exception):
    """Raised when an error occurs with the camera."""


class ModelNotFoundError(Exception):
    """Raised when a model is not found in the models/ directory."""


class InvalidMCUConfigError(Exception):
    """Raised when an invalid MCU configuration is detected."""


class MCUConnectionError(Exception):
    """Raised when an error occurs with the MCU connection."""
