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
    SHOW_STATISTICS = "sts"  # Show the statistics of the system

    GATE1_STATUS = "g1s"  # Get gate 1 status
    GATE2_STATUS = "g2s"  # Get gate 2 status
    GATE3_STATUS = "g3s"  # Get gate 3 status
    GATE4_STATUS = "g4s"  # Get gate 4 status
    COUNT_GATE5 = "ct5"  # count the object in bucket 5

    PLATFORM_STATUS = "ps"  # Get the status of the platform
    PLATFORM_OPEN = "pso"  # Open platform
    PLATFORM_CLOSE = "psc"  # Close platform

    GATE1_OPEN = "g1o"  # Open gate 1
    GATE2_OPEN = "g2o"  # Open gate 2
    GATE3_OPEN = "g3o"  # Open gate 3
    GATE4_OPEN = "g4o"  # Open gate 4
    GATE1_CLOSE = "g1c"  # Close gate 1
    GATE2_CLOSE = "g2c"  # Close gate 2
    GATE3_CLOSE = "g3c"  # Close gate 3
    GATE4_CLOSE = "g4c"  # Close gate 4

    ERR_LED_STATUS = "els"  # Error LED status
    ERR_LED_ON = "elh"  # Turn on the error LED
    ERR_LED_OFF = "ell"  # Turn off the error LED
    ACK_OBJ_SORT = "aos"  # Acknowledge object sort

    IR_STATUS = "irs"  # Get the status of the IR sensor
    IR_ACK_1 = "ir1"  # Acknowledge IR sensor 1 detection
    IR_ACK_2 = "ir2"  # Acknowledge IR sensor 2 detection
    IR_ACK_3 = "ir3"  # Acknowledge IR sensor 3 detection
    IR_ACK_4 = "ir4"  # Acknowledge IR sensor 4 detection
    IR_ACK_5 = "ir5"  # Acknowledge IR sensor 5 detection


class Responses(Enum):
    """The responses that can be received from the MCU."""

    READY = "RDY"  # The MCU is ready
    SUCCESS = "OK"  # The command was successful
    PLATFORM_SUCCESS = "OKP"  # The platform command was successful
    FAILURE = "KO"  # The command failed
    PVER_PREFIX = "PV:"  # The protocol version prefix
    GATE_OPEN = "GO"  # The gate is open
    GATE_CLOSED = "GC"  # The gate is closed
    COUNT_GATE5 = "CT"  # The object count in bucket 5
    PLATFORM_OPEN = "PO"  # The platform is open
    PLATFORM_CLOSED = "PC"  # The platform is closed
    ERR_LED_ON = "ELH"  # The error LED is on
    ERR_LED_OFF = "ELL"  # The error LED is off
    IR_STATUS = "IS:"  # IR sensor status prefix


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

        if self.connection.readline() != self._encode_command(Responses.READY):
            raise exceptions.MCUConnectionError("The MCU did not respond as expected.")

        self.logger.info("MCU connection established.")
        self.logger.info("MCU protocol version: %s", self.protocol_version)

    @property
    def protocol_version(self) -> str:
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

    @property
    def is_platform_open(self) -> bool:
        _ = self.connection.write(self._encode_command(Commands.PLATFORM_STATUS))
        return self.connection.read_until(self.sep).decode()

    @property
    def is_err_led_on(self) -> bool:
        _ = self.connection.write(self._encode_command(Commands.ERR_LED_STATUS))
        return self.connection.read_until(self.sep).decode()

    @property
    def ir_states(self) -> list[bool]:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        _ = self.connection.write(self._encode_command(Commands.IR_STATUS))
        res = self.connection.read_until(self.sep).decode()
        self.logger.debug("ir_states=%s", res)
        if not res.startswith(Responses.IR_STATUS.value):
            raise exceptions.MCUConnectionError("Invalid IR status from the MCU.")

        return [x == "1" for x in res.partition(Responses.IR_STATUS.value)[2]]

    @property
    def is_gate1_open(self) -> bool:
        _ = self.connection.write(self._encode_command(Commands.GATE1_STATUS))
        return self.connection.read_until(self.sep).decode()

    @property
    def is_gate2_open(self) -> bool:
        _ = self.connection.write(self._encode_command(Commands.GATE2_STATUS))
        return self.connection.read_until(self.sep).decode()

    @property
    def is_gate3_open(self) -> bool:
        _ = self.connection.write(self._encode_command(Commands.GATE3_STATUS))
        return self.connection.read_until(self.sep).decode()

    @property
    def is_gate4_open(self) -> bool:
        _ = self.connection.write(self._encode_command(Commands.GATE4_STATUS))
        return self.connection.read_until(self.sep).decode()

    def _encode_command(self, message: Union[Commands, Responses]) -> bytes:
        return f"{message.value}{self.sep.decode()}".encode()

    def _decode_response(self, message: bytes) -> Responses:
        return Responses(message.decode().partition(self.sep.decode())[0])

    def show_standby(self) -> None:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        _ = self.connection.write(self._encode_command(Commands.STANDBY))

        if self._decode_response(self.connection.readline()) == Responses.SUCCESS:
            self.logger.info("MCU is now in standby mode.")

        else:
            self.logger.warning("The MCU could not enter standby mode.")

    def show_statistics(self) -> None:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        _ = self.connection.write(self._encode_command(Commands.SHOW_STATISTICS))
        if self._decode_response(self.connection.readline()) == Responses.SUCCESS:
            self.logger.debug("Stats has been shown.")

        else:
            self.logger.warning("Could not show stats.")

    def set_err_led(self, turn_on: bool) -> None:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        _ = self.connection.write(
            self._encode_command(
                Commands.ERR_LED_ON if turn_on else Commands.ERR_LED_OFF
            )
        )
        _ = self.connection.read_until(self.sep)

    def acknowledge_object_sort(self) -> None:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")
        _ = self.connection.write(self._encode_command(Commands.ACK_OBJ_SORT))
        _ = self.connection.read_until(self.sep)

    def platform_activate(self):
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        _ = self.connection.write(self._encode_command(Commands.PLATFORM_OPEN))
        _ = self.connection.read_until(self.sep)

    def platform_deactivate(self):
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        _ = self.connection.write(self._encode_command(Commands.PLATFORM_CLOSE))
        _ = self.connection.read_until(self.sep)

    def set_gate_state(self, gate: int, open_gate: bool) -> None:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        if gate == 1:
            _ = self.connection.write(
                self._encode_command(
                    Commands.GATE1_OPEN if open_gate else Commands.GATE1_CLOSE
                )
            )

        elif gate == 2:
            _ = self.connection.write(
                self._encode_command(
                    Commands.GATE2_OPEN if open_gate else Commands.GATE2_CLOSE
                )
            )

        elif gate == 3:
            _ = self.connection.write(
                self._encode_command(
                    Commands.GATE3_OPEN if open_gate else Commands.GATE3_CLOSE
                )
            )

        elif gate == 4:
            _ = self.connection.write(
                self._encode_command(
                    Commands.GATE4_OPEN if open_gate else Commands.GATE4_CLOSE
                )
            )

        elif gate == 5:
            if open_gate:
                _ = self.connection.write(self._encode_command(Commands.COUNT_GATE5))

        else:
            raise ValueError("Invalid gate number.")

        _ = self.connection.read_until(self.sep)

    def acknowledge_ir_state(self, ir_number: int) -> Responses:
        if not self.connection.is_open:
            raise exceptions.MCUConnectionError("The connection is not open.")

        if ir_number == 1:
            _ = self.connection.write(self._encode_command(Commands.IR_ACK_1))
        elif ir_number == 2:
            _ = self.connection.write(self._encode_command(Commands.IR_ACK_2))
        elif ir_number == 3:
            _ = self.connection.write(self._encode_command(Commands.IR_ACK_3))
        elif ir_number == 4:
            _ = self.connection.write(self._encode_command(Commands.IR_ACK_4))
        elif ir_number == 5:
            _ = self.connection.write(self._encode_command(Commands.IR_ACK_5))
        else:
            raise ValueError("Invalid IR number.")

        return self._decode_response(self.connection.read_until(self.sep))
