"""Mock serial connection for testing without a real Pico."""

from __future__ import annotations

import random
import time
from typing import List, Optional


class MockSerial:
    """Simulates a serial connection for testing."""

    def __init__(self, port: str, baudrate: int, timeout: float) -> None:
        """Initialize mock serial connection.

        Args:
            port: Port name (ignored in mock)
            baudrate: Baud rate (ignored in mock)
            timeout: Read timeout (ignored in mock)
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.in_waiting = 0
        self._message_queue: List[str] = []
        self._last_command = ""

    def write(self, data: bytes) -> int:
        """Simulate writing to serial port.

        Args:
            data: Data to write

        Returns:
            Number of bytes written
        """
        message = data.decode().strip()
        self._last_command = message
        print(f"[MOCK] Sent: {message}")

        # Simulate responses
        if message == "HIT":
            self._message_queue.append("OK HIT")
        elif message == "MISS":
            self._message_queue.append("OK MISS")
        elif message.startswith("SCORE"):
            self._message_queue.append(f"OK {message}")
        elif message == "READY":
            self._message_queue.append("READY")
        elif message == "GAME_OVER":
            self._message_queue.append("GAME_OVER")
        else:
            self._message_queue.append(f"OK {message}")

        # Occasionally add random status messages
        if random.random() < 0.1:
            self._message_queue.append(f"[Pico] Status: {random.choice(['idle', 'processing', 'ready'])}")

        return len(data)

    def readline(self) -> bytes:
        """Read a line from the simulated serial port.

        Returns:
            Message as bytes
        """
        if self._message_queue:
            message = self._message_queue.pop(0)
            self.in_waiting = len(self._message_queue)
            return (message + "\n").encode()
        return b""

    def close(self) -> None:
        """Close the mock connection."""
        print("[MOCK] Connection closed")


class MockSerialPort:
    """Wraps MockSerial to behave like serial.Serial."""

    def __init__(self, port: str, baudrate: int = 115200, timeout: float = 0.05) -> None:
        """Initialize mock serial port.

        Args:
            port: Port name
            baudrate: Baud rate
            timeout: Read timeout
        """
        self._mock = MockSerial(port, baudrate, timeout)
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        print(f"[MOCK] Opened mock connection on {port} at {baudrate} baud")
        time.sleep(0.5)  # Simulate connection delay

    @property
    def in_waiting(self) -> int:
        """Get number of bytes waiting to be read."""
        return self._mock.in_waiting

    def write(self, data: bytes) -> int:
        """Write data to serial port.

        Args:
            data: Data to write

        Returns:
            Number of bytes written
        """
        return self._mock.write(data)

    def readline(self) -> bytes:
        """Read a line from serial port.

        Returns:
            Message as bytes
        """
        return self._mock.readline()

    def close(self) -> None:
        """Close the connection."""
        self._mock.close()
