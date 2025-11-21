from .base_scale import BaseScale
import logging

class ANDAD4401Scale(BaseScale):
    def __init__(self, name: str, device_id: str):
        super().__init__(name, device_id)
        self.terminator = b'\r\n'
        self.unit = "kg"
        self.tare_weight = 0.0
        self.mode = "GROSS" # GROSS or NET

    def process_command(self, command: bytes) -> bytes:
        """
        Handle AND AD-4401 commands.
        Protocol: ASCII, Terminator CR LF
        """
        try:
            cmd_str = command.decode('ascii', errors='ignore').strip()
        except:
            return None

        self.logger.debug(f"Received command: {cmd_str}")

        if not cmd_str:
            return None

        # Command Mode
        if cmd_str == 'RW': # Request Weight
            return self._build_weight_response()
        elif cmd_str == 'MZ': # Make Zero
            self.set_weight(0.0)
            self.tare_weight = 0.0
            return self._build_echo(cmd_str)
        elif cmd_str == 'MT': # Make Tare
            self.tare_weight = self.current_weight
            self.mode = "NET"
            return self._build_echo(cmd_str)
        elif cmd_str == 'CT': # Clear Tare
            self.tare_weight = 0.0
            self.mode = "GROSS"
            return self._build_echo(cmd_str)
        elif cmd_str == 'MG': # Make Gross
            self.mode = "GROSS"
            return self._build_echo(cmd_str)
        elif cmd_str == 'MN': # Make Net
            self.mode = "NET"
            return self._build_echo(cmd_str)
        
        # Unknown command
        return b"?E" + self.terminator

    def _build_weight_response(self) -> bytes:
        # A&D Standard Format
        # [Header1(2)][,][Header2(2)][,][Data(8)][Unit(2)][Terminator]
        # Header1: ST, US, OL
        # Header2: GS (Gross), NT (Net), TR (Tare)
        
        # Determine Header1
        if self.current_weight > 999999:
            header1 = "OL"
        elif self.is_stable:
            header1 = "ST"
        else:
            header1 = "US"

        # Determine Header2 and Value
        if self.mode == "NET":
            header2 = "NT"
            val = self.current_weight - self.tare_weight
        else:
            header2 = "GS"
            val = self.current_weight

        # Data: 8 chars including sign and dot
        # e.g. "+00123.4" (8 chars) or "+12345.6"
        # Manual example: "+0012345" (no dot?) or "+00123.45"
        # Let's assume standard float formatting to 8 chars
        # If val is 123.45 -> "+0123.45"
        
        data_str = f"{val:+08.2f}" # 8 chars? "+123.45" is 7. "+0123.45" is 8.
        if len(data_str) > 8:
             data_str = f"{val:+8.1f}" # Fallback
        
        # Unit: 2 chars
        unit_str = self.unit[:2].ljust(2) # "kg"

        response = f"{header1},{header2},{data_str}{unit_str}"
        return response.encode('ascii') + self.terminator

    def _build_echo(self, cmd: str) -> bytes:
        return cmd.encode('ascii') + self.terminator

    def _get_current_weight_data(self) -> bytes:
        return self._build_weight_response()
