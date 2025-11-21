from .base_scale import BaseScale
import logging

class CasNT301AScale(BaseScale):
    def __init__(self, name: str, device_id: str):
        super().__init__(name, device_id)
        self.terminator = b'\r\n'
        self.unit = "kg"
        self.tare_weight = 0.0
        self._current_format = "Format 1" # Default 18 bytes
        self.device_id_str = "01" # Default Device ID "01"

    @property
    def available_formats(self):
        return ["Format 1", "Format 2"] # 18 bytes, 22 bytes

    def set_format(self, format_name: str):
        if format_name in self.available_formats:
            self._current_format = format_name
            super().set_format(format_name)
        else:
            self.logger.warning(f"Invalid format: {format_name}")

    def process_command(self, command: bytes) -> bytes:
        """
        Handle CAS NT-301A commands.
        Supports Simple Command Mode (F33=5)
        """
        try:
            cmd_str = command.decode('ascii', errors='ignore').strip()
        except:
            return None

        self.logger.debug(f"Received command: {cmd_str}")

        if not cmd_str:
            return None

        # Simple Command Mode: "dd RW" where dd is device ID
        # Check if command starts with device ID
        if len(cmd_str) >= 5 and cmd_str[:2] == self.device_id_str:
            cmd_body = cmd_str[3:] # "RW", "MZ", "MT"
            
            if cmd_body == 'RW':
                return self._build_weight_response()
            elif cmd_body == 'MZ':
                self.set_weight(0.0)
                self.tare_weight = 0.0
                return self._build_echo(cmd_str)
            elif cmd_body == 'MT':
                self.tare_weight = self.current_weight
                return self._build_echo(cmd_str)
            elif cmd_body.startswith('PN'): # PN 00
                return self._build_echo(cmd_str)
        
        return None

    def _build_weight_response(self) -> bytes:
        # Format 1 (18 Bytes): [Header1(2)][,][Header2(2)][,][Data(8)][Unit(2)][CR][LF]
        # Format 2 (22 Bytes): [Header1(2)][,][Header2(2)][,][Lamp(1)][Data(8)][Space(1)][Unit(2)][CR][LF]

        # Header1
        if self.current_weight > 999999:
            header1 = "OL"
        elif self.is_stable:
            header1 = "ST"
        else:
            header1 = "US"

        # Header2
        if self.tare_weight > 0:
            header2 = "NT"
            val = self.current_weight - self.tare_weight
        else:
            header2 = "GS"
            val = self.current_weight

        # Data: 8 chars including sign and dot
        # e.g. "+00123.4"
        data_str = f"{val:+08.1f}" # 8 chars
        if len(data_str) > 8:
             data_str = f"{val:+8.0f}" # Fallback

        # Unit: 2 chars
        unit_str = self.unit[:2].ljust(2) # "kg"

        if self._current_format == "Format 1":
            # [Header1(2)][,][Header2(2)][,][Data(8)][Unit(2)]
            response = f"{header1},{header2},{data_str}{unit_str}"
            return response.encode('ascii') + self.terminator

        elif self._current_format == "Format 2":
            # [Header1(2)][,][Header2(2)][,][Lamp(1)][Data(8)][Space(1)][Unit(2)]
            # Lamp: 1 byte. 
            # bit6: Stable(1), bit0: Zero(1), bit1: Tare(1) ...
            # Let's use '0' (0x30) as base and add bits? 
            # Protocol says "Lamp(1)". Usually ASCII char representing status.
            # Let's simulate a simple status char '0' or specific bits if needed.
            # For now, fixed '0'.
            lamp = '0'
            response = f"{header1},{header2},{lamp}{data_str} {unit_str}"
            return response.encode('ascii') + self.terminator

        return None

    def _build_echo(self, cmd: str) -> bytes:
        return cmd.encode('ascii') + self.terminator

    def _get_current_weight_data(self) -> bytes:
        return self._build_weight_response()
