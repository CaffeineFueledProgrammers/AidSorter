import multiprocessing

from aidsorter import exceptions
from aidsorter.logger import LoggerFactory


class MCUConfig:
    """A helper class to easily process the MCU configuration file."""

    def __init__(self, config_path: str) -> None:
        """Create a new MCUConfig object.

        Args:
            config_path: The path of the configuration file.
        """

        self.__logger = LoggerFactory().get_logger(__name__)
        self.__config_path = config_path
        self.__logger.info("Reading configuration file: %s", config_path)
        with open(config_path, "r", encoding="utf-8") as config_file:
            contents = config_file.readlines()

        # These are the default values so it's fine to redeclare them.
        self.resolution: tuple[int, int] = (  # pyright: ignore[reportRedeclaration]
            640,
            480,
        )
        bucket1_contents: tuple[str, ...] = ()  # pyright: ignore[reportRedeclaration]
        bucket2_contents: tuple[str, ...] = ()  # pyright: ignore[reportRedeclaration]
        bucket3_contents: tuple[str, ...] = ()  # pyright: ignore[reportRedeclaration]
        bucket4_contents: tuple[str, ...] = ()  # pyright: ignore[reportRedeclaration]

        for line in contents:
            self.__logger.debug("Processing line: %s", line.replace("\n", "\\n"))
            if line.startswith("#") or line.strip() == "":
                # self.__logger.debug("Skipping line...")
                continue  # Skip comments and empty lines

            key, _, value = line.strip().partition("=")
            if key == "cpu_threads":
                self.__cpu_threads = int(value)
                if self.__cpu_threads < 1:
                    self.__cpu_threads = multiprocessing.cpu_count()

            elif key == "resolution":
                self.resolution: tuple[int, int] = (
                    int(value.partition("x")[0]),
                    int(value.partition("x")[2]),
                )

            elif key == "detector_debounce":
                self.__detector_debounce = int(value)

            elif key == "detector_samples":
                self.__detector_samples: int = int(value)

            elif key == "baudrate":
                self.__baudrate = int(value)

            elif key == "mcu_connection_timeout":
                self.mcu_connection_timeout: float = float(value)

            elif key == "bucket1_contents":
                bucket1_contents: tuple[str, ...] = (
                    tuple(value.split(",")) if len(value) > 0 else ()
                )

            elif key == "bucket2_contents":
                bucket2_contents: tuple[str, ...] = (
                    tuple(value.split(",")) if len(value) > 0 else ()
                )

            elif key == "bucket3_contents":
                bucket3_contents: tuple[str, ...] = (
                    tuple(value.split(",")) if len(value) > 0 else ()
                )

            elif key == "bucket4_contents":
                bucket4_contents: tuple[str, ...] = (
                    tuple(value.split(",")) if len(value) > 0 else ()
                )

            else:
                raise exceptions.InvalidMCUConfigError(f"Unknown config key: {key}")

        self.bucket_contents: tuple[
            tuple[str, ...], tuple[str, ...], tuple[str, ...], tuple[str, ...]
        ] = (
            bucket1_contents,
            bucket2_contents,
            bucket3_contents,
            bucket4_contents,
        )

        self.__logger.info("Configuration loaded successfully.")
        self.__logger.info("\tCPU Threads: %s", self.cpu_threads)
        self.__logger.info("\tResolution: %s", self.resolution)
        self.__logger.info("\tDetector Debounce: %s", self.detector_debounce)
        self.__logger.info("\tBaudrate: %s", self.baudrate)
        self.__logger.info("\tBucket 1 has %s item/s", len(self.bucket_contents[0]))
        self.__logger.info("\tBucket 2 has %s item/s", len(self.bucket_contents[1]))
        self.__logger.info("\tBucket 3 has %s item/s", len(self.bucket_contents[2]))
        self.__logger.info("\tBucket 4 has %s item/s", len(self.bucket_contents[3]))

        self.__logger.debug("\tBucket 1 contents: %s", self.bucket_contents[0])
        self.__logger.debug("\tBucket 2 contents: %s", self.bucket_contents[1])
        self.__logger.debug("\tBucket 3 contents: %s", self.bucket_contents[2])
        self.__logger.debug("\tBucket 4 contents: %s", self.bucket_contents[3])

    @property
    def config_path(self) -> str:
        """Get the path of the configuration file.

        Returns:
            The path of the configuration file.
        """

        return self.__config_path

    @property
    def detector_debounce(self) -> int:
        """Get the debounce value in frames for the system to wait
        before registering a new object detection.
        Returns:
            The debounce value in frames.
        """

        return self.__detector_debounce

    @property
    def detector_samples(self) -> int:
        """How many samples should the program take before
        considering the object as something that belongs
        to a bucket.
        Returns:
            The number of samples to take for object detection.
        """

        return self.__detector_samples

    @property
    def baudrate(self) -> int:
        """Get the baudrate of the MCU.
        Returns:
            The baudrate of the MCU.
        """

        return self.__baudrate

    @property
    def cpu_threads(self) -> int:
        """Get the number of CPU threads to use.

        Returns:
            The number of CPU threads to use.
        """

        return self.__cpu_threads
