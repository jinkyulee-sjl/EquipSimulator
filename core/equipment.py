from abc import ABC, abstractmethod
import logging

class Equipment(ABC):
    def __init__(self, name: str, device_id: str, model: str = ""):
        self.name = name
        self.device_id = device_id
        self.model = model
        self.connected = False
        self.logger = logging.getLogger(f"Equipment.{name}")
        self.on_output = None
        self.connection_settings = {
            "port": "COM1",
            "baudrate": 9600,
            "bytesize": 8,
            "parity": "None",
            "stopbits": 1
        }

    @abstractmethod
    def process_command(self, command: bytes) -> bytes:
        """
        Process an incoming command and return the response.
        If no response is needed, return None or empty bytes.
        """
        pass

    def connect(self):
        self.connected = True
        self.logger.info(f"{self.name} connected.")

    def disconnect(self):
        self.connected = False
        self.logger.info(f"{self.name} disconnected.")
