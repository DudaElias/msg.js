"""Serial communication with Raspberry Pi Pico."""

from __future__ import annotations

import sys
import time
from typing import List, Optional

import serial
from serial.tools import list_ports

from pc.utils.config import DEFAULT_BAUD_RATE, SERIAL_INIT_DELAY, SERIAL_TIMEOUT
from .mock_serial import MockSerialPort


class PicoLink:
    """Handles serial communication with the Pico."""

    def __init__(self, port: Optional[str], baud: int = DEFAULT_BAUD_RATE, use_mock: bool = False) -> None:
        """Initialize serial connection.

        Args:
            port: Serial port name (e.g., 'COM5', '/dev/ttyUSB0')
            baud: Baud rate for serial communication
            use_mock: If True, use mock serial connection for testing
        """
        self.connection: Optional[serial.Serial] = None
        self.use_mock = use_mock

        if port:
            try:
                if use_mock:
                    self.connection = MockSerialPort(port, baud, timeout=SERIAL_TIMEOUT)
                else:
                    self.connection = serial.Serial(port, baud, timeout=SERIAL_TIMEOUT)
                time.sleep(SERIAL_INIT_DELAY)
            except serial.SerialException as exc:
                print(f"Could not open {port}: {exc}", file=sys.stderr)
                self.connection = None

    def send(self, command: str) -> None:
        """Send a command to the Pico.

        Args:
            command: Command string to send
        """
        if self.connection is None:
            return
        try:
            self.connection.write((command + "\n").encode())
        except serial.SerialException:
            self.connection = None

    def read_messages(self) -> List[str]:
        """Read all available messages from the Pico.

        Returns:
            List of message strings
        """
        messages: List[str] = []
        if self.connection is None:
            return messages

        try:
            while self.connection.in_waiting:
                message = self.connection.readline().decode(errors="replace").strip()
                if message:
                    messages.append(message)
        except serial.SerialException:
            self.connection = None

        return messages

    def close(self) -> None:
        """Close the serial connection."""
        if self.connection is not None:
            self.connection.close()
            self.connection = None

    @staticmethod
    def list_available_ports() -> None:
        """Print available serial ports."""
        ports = [port.device for port in list_ports.comports()]
        if ports:
            print("Available serial ports:")
            for port in ports:
                print(f"  {port}")
        else:
            print("No serial ports were detected.")
