import json
import logging
from typing import Dict, Any
from datetime import datetime

class ProjectManager:
    """Handles saving and loading of project files (.ESPJ)"""
    
    def __init__(self):
        self.logger = logging.getLogger("ProjectManager")
        self.version = "1.0"
    
    def save_project(self, simulator, filepath: str) -> bool:
        """
        Save current simulator state to a project file.
        
        Args:
            simulator: Simulator instance
            filepath: Path to save the .ESPJ file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            project_data = {
                "version": self.version,
                "created": datetime.now().isoformat(),
                "devices": []
            }
            
            # Serialize each device
            for name, device in simulator.devices.items():
                device_data = {
                    "name": name,
                    "model": device.model,
                    "device_id": device.device_id,
                    "connection_settings": device.connection_settings.copy(),
                    "current_weight": device.current_weight if hasattr(device, 'current_weight') else 0.0,
                    "is_stable": device.is_stable if hasattr(device, 'is_stable') else True,
                }
                
                # Add scale-specific settings
                if hasattr(device, 'current_format'):
                    device_data["current_format"] = device.current_format
                if hasattr(device, 'print_mode'):
                    device_data["print_mode"] = device.print_mode
                if hasattr(device, 'weight_range'):
                    device_data["weight_range"] = device.weight_range
                if hasattr(device, '_current_command_mode'):
                    device_data["command_mode"] = device._current_command_mode
                if hasattr(device, '_use_bcc'):
                    device_data["use_bcc"] = device._use_bcc
                    
                project_data["devices"].append(device_data)
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(project_data, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"Project saved to {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save project: {e}")
            return False
    
    def load_project(self, simulator, filepath: str) -> bool:
        """
        Load project from file and restore simulator state.
        
        Args:
            simulator: Simulator instance
            filepath: Path to the .ESPJ file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                project_data = json.load(f)
            
            # Validate version
            if project_data.get("version") != self.version:
                self.logger.warning(f"Project version mismatch: {project_data.get('version')} vs {self.version}")
            
            # Clear existing devices
            device_names = list(simulator.devices.keys())
            for name in device_names:
                if name in simulator.devices:
                    # Disconnect device to stop any streaming threads
                    device = simulator.devices[name]
                    if hasattr(device, 'disconnect'):
                        device.disconnect()
                    del simulator.devices[name]
            
            # Recreate devices
            for device_data in project_data.get("devices", []):
                name = device_data["name"]
                model = device_data["model"]
                device_id = device_data["device_id"]
                
                # Create device
                if simulator.create_device(model, name, device_id):
                    device = simulator.get_device(name)
                    
                    # Restore settings
                    conn_settings = device_data.get("connection_settings", {})
                    # Convert parity from display format to storage format if needed
                    parity_convert = {"None": 'N', "Even": 'E', "Odd": 'O', "Mark": 'M', "Space": 'S'}
                    if "parity" in conn_settings and conn_settings["parity"] in parity_convert:
                        conn_settings["parity"] = parity_convert[conn_settings["parity"]]
                    device.connection_settings = conn_settings
                    
                    if hasattr(device, 'current_weight'):
                        device.current_weight = device_data.get("current_weight", 0.0)
                    if hasattr(device, 'is_stable'):
                        device.is_stable = device_data.get("is_stable", True)
                    if hasattr(device, 'current_format') and "current_format" in device_data:
                        device.current_format = device_data["current_format"]
                    if hasattr(device, 'print_mode') and "print_mode" in device_data:
                        device.print_mode = device_data["print_mode"]
                    if hasattr(device, 'weight_range') and "weight_range" in device_data:
                        device.weight_range = device_data["weight_range"]
                    if hasattr(device, 'set_command_mode') and "command_mode" in device_data:
                        device.set_command_mode(device_data["command_mode"])
                    if hasattr(device, 'set_use_bcc') and "use_bcc" in device_data:
                        device.set_use_bcc(device_data["use_bcc"])
                else:
                    self.logger.error(f"Failed to create device: {name} ({model})")
            
            self.logger.info(f"Project loaded from {filepath}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load project: {e}")
            return False
