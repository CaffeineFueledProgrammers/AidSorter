from typing import Optional


class FPSConfig:
    """A helper class to easily process FPS values."""

    def __init__(self, history_len: int = 1000, avg_frame_count: int = 10) -> None:
        """Create a new FPSConfig object.

        Args:
            history_len: The length of the FPS history.
            avg_frame_count: Get the average of the last <avg_frame_count> frames.
        """

        self.frame_count: int = 0  # The current frame count
        self.start_time: float = 0.0
        self.end_time: float = 0.0
        self.latest_fps: float = 0.0  # The latest FPS value
        self.__fps: list[float] = []
        self.__history_len = history_len
        self.__avg_frame_count: int = avg_frame_count

    @property
    def history(self) -> list[float]:
        """Get the FPS history.

        Returns:
            The FPS history.
        """

        return self.__fps

    @property
    def history_len(self) -> int:
        """Get the length limit of the FPS history.

        Returns:
            The length limit of the FPS history.
        """

        return self.__history_len

    @property
    def avg_frame_count(self) -> int:
        """Get the frame count for the average FPS.

        Returns:
            The frame count for the average FPS.
        """

        return self.__avg_frame_count

    @property
    def minimum(self) -> Optional[float]:
        """Get the minimum FPS value.

        Returns:
            The minimum FPS value.
        """

        return min(self.__fps) if self.__fps else None

    @property
    def maximum(self) -> Optional[float]:
        """Get the maximum FPS value.

        Returns:
            The maximum FPS value.
        """

        return max(self.__fps) if self.__fps else None

    @property
    def average(self) -> Optional[float]:
        """Get the average FPS value.

        Returns:
            The average FPS value.
        """

        return sum(self.__fps) / len(self.__fps) if self.__fps else None

    def add_record(self, fps: float) -> None:
        """Add a new FPS record to the history.

        Args:
            fps: The FPS value to add.
        """

        self.__fps = self.__fps[-self.__history_len :] + [fps]
