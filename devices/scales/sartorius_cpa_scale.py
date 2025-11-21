from .base_scale import BaseScale
import logging

class SartoriusCPAScale(BaseScale):
    def __init__(self, name: str, device_id: str):
        super().__init__(name, device_id)
        self.terminator = b'\r\n'
        self.unit = "g"
        self._current_format = "Format 1" # Default 16 chars

    @property
    def available_formats(self):
        return ["Format 1", "Format 2"] # 16 bytes, 22 bytes

    def set_format(self, format_name: str):
        if format_name in self.available_formats:
            self._current_format = format_name
            super().set_format(format_name)
        else:
            self.logger.warning(f"Invalid format: {format_name}")

    def process_command(self, command: bytes) -> bytes:
        """
        Handle Sartorius CPA Series commands.
        Protocol: Starts with ESC (0x1B), Ends with CR LF
        """
        try:
            cmd_str = command.decode('ascii', errors='ignore').strip()
        except:
            return None

        self.logger.debug(f"Received command: {cmd_str}")

        if not cmd_str:
            return None

        # Check for ESC prefix (ASCII 27 -> \x1b)
        if len(cmd_str) < 2:
            return None

        if cmd_str[0] == '\x1b':
            cmd_char = cmd_str[1]
            
            if cmd_char == 'P': # Print
                return self._build_weight_response()
            elif cmd_char == 'T': # Tare / Zero
                self.set_weight(0.0)
                return None
            elif cmd_char == 'Z': # Internal Cal
                return None
            elif cmd_char == 'S': # Restart
                return None
            # ... other commands ...
        
        return None

    def _build_weight_response(self) -> bytes:
        # Sartorius CPA Format
        # Format 1 (16 chars): [Sign(1)][Space(1)][Data(8)][Space(1)][Unit(3)][CR][LF]
        # Format 2 (22 chars): [ID(6)][Sign(1)][Space(1)][Data(8)][Space(1)][Unit(3)][CR][LF]
        
        # Check for Overload
        if self.current_weight > 999999:
            # Special code: "Stat H" (Overload)
            # Format 1: "Stat H  " ? Manual says "Stat H"
            # Let's assume standard error text fitting the length
            return b"Stat H         \r\n"

        # Sign
        sign = "+" if self.current_weight >= 0 else "-"
        
        # Data (8 chars)
        # e.g. "  123.45"
        weight_val = abs(self.current_weight)
        data_str = f"{weight_val:8.2f}" # 8 chars
        if len(data_str) > 8:
             data_str = f"{weight_val:8.1f}"

        # Unit (3 chars)
        unit_str = self.unit.ljust(3) # "g  "

        # Construct Response
        # Format 1: [Sign(1)][Space(1)][Data(8)][Space(1)][Unit(3)] = 14 chars + CR LF = 16
        base_resp = f"{sign} {data_str} {unit_str}"
        
        if self._current_format == "Format 2":
            # Add ID (6 chars)
            # ID: "N     " (Net?) or "Stat  "
            # Let's use "N     " for normal weight
            id_str = "N     "
            base_resp = f"{id_str}{base_resp}"

        return base_resp.encode('ascii') + self.terminator

    def _get_current_weight_data(self) -> bytes:
        return self._build_weight_response()
