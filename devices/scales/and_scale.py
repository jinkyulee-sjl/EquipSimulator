from .base_scale import BaseScale
import logging

class ANDScale(BaseScale):
    def __init__(self, name: str, device_id: str, model: str = "AD-4401"):
        super().__init__(name, device_id)
        self.model = model
        self.terminator = b'\r\n'

    def process_command(self, command: bytes) -> bytes:
        """
        Handle AND AD-4401 commands.
        Common commands:
        'Q': Request weight (Immediate)
        'Z': Zero
        """
        cmd_str = command.decode('ascii', errors='ignore').strip()
        self.logger.debug(f"Received command: {cmd_str}")

        if cmd_str == 'Q' or cmd_str == 'RW':
            return self._build_weight_response()
        elif cmd_str == 'Z':
            self.set_weight(0.0)
            return None # Z usually doesn't return data immediately in some modes, or returns ACK
        
        return None

    def _build_weight_response(self) -> bytes:
        # Format: ST,GS,+00123.4kg
        # ST: Stable, US: Unstable
        # GS: Gross Weight, NT: Net Weight
        
        header1 = "ST" if self.is_stable else "US"
        header2 = "GS" # Assuming Gross weight for now
        
        # Format weight to 7 chars (including sign and dot), e.g., "+00123.4"
        # AD-4401 manual usually specifies:
        # <HEADER1>,<HEADER2>,<DATA>(8 digits including sign/dot),<UNIT>
        # Example: ST,GS,+00123.4kg
        
        weight_str = f"{self.current_weight:+08.1f}" # +00123.4 (8 chars)
        
        response = f"{header1},{header2},{weight_str}{self.unit}"
        return response.encode('ascii') + self.terminator
