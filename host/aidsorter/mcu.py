"""AidSorter - Automatic Goods Sorting System

This module contains the system that handles camera features.
"""

# pyright: reportDeprecated=false

from enum import Enum
from typing import Union

import serial

from aidsorter import exceptions, info
from aidsorter.logger import LoggerFactory


class Commands(Enum):
    """The commands that can be sent to the MCU."""

    GET_PROTOCOL_VERSION = "pro"  # Get the MCU's protocol version
    STANDBY = "stb"  # Put the MCU in standby mode
    
    GATE1_STATUS = "g1s"  # Get gate 1 status
    GATE2_STATUS = "g2s"  # Get gate 2 status
    GATE3_STATUS = "g3s"  # Get gate 3 status
    GATE4_STATUS = "g4s"  # Get gate 4 status
    GATE1_OPEN = "g1o"  # Open gate 1
    GATE2_OPEN = "g2o"  # Open gate 2
    GATE3_OPEN = "g3o"  # Open gate 3
    GATE4_OPEN = "g4o"  # Open gate 4
    # GATE1_CLOSE = "g1c"  # Close gate 1
    # GATE2_CLOSE = "g2c"  # Close gate 2
    # GATE3_CLOSE = "g3c"  # Close gate 3
    # GATE4_CLOSE = "g4c"  # Close gate 4


class Responses(Enum):
    """The responses that can be received from the MCU."""

    READY = "RDY"  # The MCU is ready
    SUCCESS = "OK"  # The command was successful
    FAILURE = "KO"  # The command failed
    PVER_PREFIX = "PV:"  # The protocol version prefix
    GATE_OPEN = "GO"  # The gate is open
    GATE_CLOSED = "GC"  # The gate is closed


class MCU:
    def __init__(
        self, port: str = "/dev/ttyUSB0", baudrate: int = 9600, timeout: float = 10.0
    ) -> None:
        self.connection = serial.Serial(port, baudrate, timeout=timeout)
        self.sep = info.PROTOCOL_SEP.encode()
        self.logger = LoggerFactory().get_logger(__name__)

        self.logger.info("Checking for MCU connection...")
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("Could not connect to the MCU.")

        if self._decode_response(self.connection.readline()) != Responses.READY:
            raise exceptions.MCUConnectionError("The MCU did not respond as expected.")

        self.logger.info("MCU connection established.")
        self.logger.info("MCU protocol version: %s", self.get_protocol_version())

    def _encode_command(self, message: Union[Commands, Responses]) -> bytes:
        return f"{message.value}{self.sep.decode()}".encode()

    def _decode_response(self, message: bytes) -> Responses:
        return Responses(message.decode().partition(self.sep.decode())[0])

    def get_protocol_version(self) -> str:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        _ = self.connection.write(self._encode_command(Commands.GET_PROTOCOL_VERSION))
        protocol_version = (
            self.connection.read_until(self.sep)
            .decode()
            .partition(self.sep.decode())[0]
            .partition(Responses.PVER_PREFIX.value)[2]
        )
        return protocol_version

    def standby(self) -> None:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        _ = self.connection.write(self._encode_command(Commands.STANDBY))

        if self._decode_response(self.connection.readline()) == Responses.SUCCESS:
            self.logger.info("MCU is now in standby mode.")

        else:
            self.logger.warning("The MCU could not enter standby mode.")

    # def get_gate_status(self) -> int:
    #     if not self.connection.is_open:
    #         raise exceptions.MCUConnectionError("The connection is not open.")
    #     gate_status = self.connection.readline().decode().strip()
    #     return int(gate_status)

    def put_object(self, gate: int) -> None:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        if gate == 1:
            _ = self.connection.write(self._encode_command(Commands.GATE1_OPEN))

        elif gate == 2:
            _ = self.connection.write(self._encode_command(Commands.GATE2_OPEN))

        elif gate == 3:
            _ = self.connection.write(self._encode_command(Commands.GATE3_OPEN))

        elif gate == 4:
            _ = self.connection.write(self._encode_command(Commands.GATE4_OPEN))

        elif gate == 5:
           
            # TODO: allow the object to fall to the end of the conveyor belt
            pass

        else:
            raise exceptions.InvalidMCUConfigError("Invalid gate number.")
