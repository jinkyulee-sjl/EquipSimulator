from typing import List, Dict
from .equipment import Equipment
from .comm_manager import CommManager
import logging

class Simulator:
    def __init__(self):
        self.devices: Dict[str, Equipment] = {}
        self.comm_manager = CommManager()
        self.logger = logging.getLogger("Simulator")

    def add_device(self, device: Equipment):
        self.devices[device.name] = device
        self.logger.info(f"Added device: {device.name}")

    def get_device(self, name: str) -> Equipment:
        return self.devices.get(name)

    def start_device_comm(self, device_name: str, port: str, baudrate: int = 9600, bytesize: int = 8, parity: str = 'N', stopbits: float = 1):
        device = self.get_device(device_name)
        if not device:
            self.logger.error(f"Device {device_name} not found")
            return False

        # Callback for serial data
        def on_data_received(data: bytes) -> bytes:
            return device.process_command(data)

        # Callback for streaming data
        def on_device_output(data: bytes):
            self.comm_manager.write(port, data)
        
        device.on_output = on_device_output

        return self.comm_manager.start_serial(port, baudrate, bytesize, parity, stopbits, on_data_received)

    def stop_device_comm(self, device_name: str):
        # We need to find which port this device is using.
        # Currently Simulator doesn't track device->port mapping explicitly, 
        # but we can infer it or store it.
        # For now, let's assume the UI passes the port or we store it.
        # Wait, the UI calls start_device_comm with port.
        # Let's modify start_device_comm to store the port mapping.
        pass 

    def stop_device_comm_by_port(self, port: str):
        return self.comm_manager.stop_serial(port)

    def stop(self):
        self.comm_manager.stop_all()
