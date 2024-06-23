"""AidSorter - Automatic Goods Sorting System

This module contains all custom exceptions
"""


class CameraError(Exception):
    """Raised when an error occurs with the camera."""


class ModelNotFoundError(Exception):
    """Raised when a model is not found in the models/ directory."""
