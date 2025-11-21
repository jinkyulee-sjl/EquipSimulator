from typing import List, Dict
from .equipment import Equipment
from .comm_manager import CommManager
import logging

class Simulator:
    def __init__(self):
        self.devices: Dict[str, Equipment] = {}
        self.device_types: Dict[str, tuple] = {} # name -> (class, default_kwargs)
        self.comm_manager = CommManager()
        self.logger = logging.getLogger("Simulator")

    def register_device_type(self, type_name: str, device_class: type, **kwargs):
        """
        Register a device class that can be instantiated by the user.
        :param type_name: Display name for the device type
        :param device_class: The class to instantiate
        :param kwargs: Default arguments to pass to the constructor (excluding name/id)
        """
        self.device_types[type_name] = (device_class, kwargs)
        self.logger.info(f"Registered device type: {type_name}")

    def create_device(self, type_name: str, name: str, device_id: str) -> bool:
        if type_name not in self.device_types:
            return False
        
        cls, defaults = self.device_types[type_name]
        try:
            # Merge defaults with specific name/id
            # Assuming constructor signature is (name, device_id, **kwargs) or similar
            # But our BaseScale is (name, device_id). Some might have extra args.
            device = cls(name, device_id, **defaults)
            device.model = type_name
            self.add_device(device)
            return True
        except Exception as e:
            self.logger.error(f"Failed to create device {name} of type {type_name}: {e}")
            return False

    def update_device(self, old_name: str, new_name: str, new_model: str) -> bool:
        if old_name not in self.devices:
            return False
        
        old_device = self.devices[old_name]
        
        # If model changed, we need to recreate the device
        if old_device.model != new_model:
            if new_model not in self.device_types:
                return False
            
            # Preserve settings if possible
            settings = old_device.connection_settings
            
            # Remove old
            self.devices.pop(old_name)
            
            # Create new
            # Reuse ID for now or generate new? Let's reuse ID if possible or just make new one based on name
            new_id = new_name.upper().replace(" ", "_")
            if self.create_device(new_model, new_name, new_id):
                new_device = self.devices[new_name]
                new_device.connection_settings = settings
                self.logger.info(f"Updated device {old_name} -> {new_name} ({new_model})")
                return True
            else:
                # Restore old if fail?
                self.devices[old_name] = old_device
                return False
        
        # If only name changed
        elif old_name != new_name:
            if new_name in self.devices:
                return False
            self.devices.pop(old_name)
            old_device.name = new_name
            self.devices[new_name] = old_device
            self.logger.info(f"Renamed device {old_name} to {new_name}")
            return True
            
        return True

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
