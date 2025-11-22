from .base_scale import BaseScale
import logging

class SartoriusBPScale(BaseScale):
    def __init__(self, name: str, device_id: str):
        super().__init__(name, device_id)
        self.terminator = b'\r\n'
        self.unit = "g" # Default unit
        self._current_format = "16 Byte"

    @property
    def available_formats(self):
        return ["16 Byte", "22 Byte"]

    def set_format(self, format_name: str):
        if format_name in self.available_formats:
            self._current_format = format_name
            super().set_format(format_name)

    def process_command(self, command: bytes) -> bytes:
        """
        Handle Sartorius BP Series commands.
        Protocol: Starts with ESC (0x1B), Ends with CR LF
        """
        try:
            # Decode assuming ASCII. 
            # Note: command usually includes ESC. 
            # We need to handle ESC char carefully or strip it.
            cmd_str = command.decode('ascii', errors='ignore').strip()
        except:
            return None

        self.logger.debug(f"Received command: {cmd_str}")

        if not cmd_str:
            return None

        # Check for ESC prefix (ASCII 27 -> \x1b)
        # cmd_str might look like "\x1bP"
        
        if len(cmd_str) < 2:
            return None

        # Sartorius commands start with ESC
        if cmd_str[0] == '\x1b':
            cmd_char = cmd_str[1]
            
            if cmd_char == 'P': # Print
                return self._build_weight_response()
            elif cmd_char == 'T': # Tare / Zero
                self.set_weight(0.0)
                return None # Usually no immediate response, or maybe just weight output if auto-print?
            elif cmd_char == 'Z': # Internal Cal
                return None
            elif cmd_char == 'S': # Restart
                return None
            # ... other commands ...
        
        return None

    def _build_weight_response(self) -> bytes:
        # Sartorius BP Format
        # Format 1 (16 chars): [Sign(1)][Data(10)][Unit(3)][CR][LF]
        # Format 2 (22 chars): [ID(6)][Sign(1)][Data(10)][Unit(3)][CR][LF]
        
        if self.current_weight > 999999: # Overload
            # Special code for overload
            # 16 Byte: "        High   " (14 chars + CR LF)
            base_resp = "        High  "
            if self._current_format == "22 Byte":
                 # ID(6) + base
                 base_resp = "Stat  " + base_resp
            return base_resp.encode('ascii') + self.terminator

        # Sign
        sign = "+" if self.current_weight >= 0 else "-"
        if self.current_weight == 0: sign = " " # Or +? Manual example shows +

        # Data (10 chars)
        # e.g. "    123.45"
        weight_val = abs(self.current_weight)
        data_str = f"{weight_val:10.2f}" # 10 chars, 2 decimals
        if len(data_str) > 10:
             data_str = f"{weight_val:10.1f}"

        # Unit (3 chars)
        unit_str = self.unit.ljust(3) # "g  "

        # Construct Base Response (14 chars)
        base_resp = f"{sign}{data_str}{unit_str}"
        
        if self._current_format == "22 Byte":
            # Add ID (6 chars)
            # ID: "N     " (Net?) or "Stat  "
            id_str = "N     "
            base_resp = f"{id_str}{base_resp}"

        return base_resp.encode('ascii') + self.terminator

    def _get_current_weight_data(self) -> bytes:
        return self._build_weight_response()
