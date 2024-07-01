"""AidSorter - Automatic Goods Sorting System

This module contains the system that handles camera features.
"""

import serial

from aidsorter import exceptions
from aidsorter.logger import LoggerFactory


class MCU:
    def __init__(
        self, port: str = "/dev/ttyUSB0", baudrate: int = 9600, timeout: float = 10.0
    ) -> None:
        self.connection = serial.Serial(port, baudrate, timeout=timeout)
        self.logger = LoggerFactory().get_logger(__name__)

        self.logger.info("Checking for MCU connection...")
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("Could not connect to the MCU.")

        if self.connection.readline() != b"OK\n":
            raise exceptions.MCUConnectionError("The MCU did not respond as expected.")

        self.logger.info("MCU connection established.")

    # def get_gate_status(self) -> int:
    #     if not self.connection.is_open:
    #         raise exceptions.MCUConnectionError("The connection is not open.")
    #     gate_status = self.connection.readline().decode().strip()
    #     return int(gate_status)

    def put_object(self, gate: int) -> None:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        if gate not in range(1, 6):
            raise exceptions.InvalidMCUConfigError("Invalid gate number.")

        _ = self.connection.write(f"{str(gate)}\n".encode())
