from .base_scale import BaseScale
import logging

class ANDGPScale(BaseScale):
    def __init__(self, name: str, device_id: str):
        super().__init__(name, device_id)
        self.terminator = b'\r\n'
        # A&D GP supports various units, default to 'g' or 'kg'
        self.unit = "kg" 

    def process_command(self, command: bytes) -> bytes:
        """
        Handle AND GP Series commands.
        Protocol: ASCII, Terminator CR LF
        """
        try:
            cmd_str = command.decode('ascii', errors='ignore').strip()
        except:
            return None

        self.logger.debug(f"Received command: {cmd_str}")

        if not cmd_str:
            return None

        # Data Query Commands
        if cmd_str == 'Q' or cmd_str == 'SI': # Immediate Query
            return self._build_weight_response()
        elif cmd_str == 'S': # Stable Query
            # In a real device, this waits for stability. 
            # Here we simulate immediate response if stable, or nothing/wait if unstable?
            # For simplicity in simulator, we return immediately but mark as unstable if needed,
            # or better: only return if stable.
            if self.is_stable:
                return self._build_weight_response()
            else:
                return None # Ignore or wait (simulator logic usually simplifies this)
        
        # Control Commands
        elif cmd_str == 'R' or cmd_str == 'Z': # Re-Zero / Zero
            self.set_weight(0.0)
            return self._build_ack() # Optional: Some settings return ACK
        elif cmd_str == 'CAL':
            # Simulate calibration (just a delay or ACK)
            return self._build_ack()
        elif cmd_str == 'OFF':
            # Simulate Display OFF
            return self._build_ack()
        elif cmd_str == 'ON' or cmd_str == 'P':
            # Simulate Display ON
            return self._build_ack()
        elif cmd_str == 'PRT':
            # Print command
            return self._build_weight_response()
        
        # Unknown command
        return self._build_error("E01")

    def _build_weight_response(self) -> bytes:
        # A&D Standard Format
        # [Header(2)][,][Data(9)][Unit(3)][Terminator(2)]
        # Header: ST (Stable), US (Unstable), OL (Overload)
        # Data: 9 chars including sign, right aligned
        # Unit: 3 chars (e.g., ' kg', '  g')

        if self.current_weight > 999999: # Simple overload check
            header = "OL"
        elif self.is_stable:
            header = "ST"
        else:
            header = "US"

        # Format weight: 9 chars, e.g., "+0012.345"
        # Assuming 3 decimal places for kg/g usually, but depends on capacity.
        # Let's use generic formatting.
        weight_val = self.current_weight
        data_str = f"{weight_val:+09.3f}" # +0012.345 (9 chars)
        if len(data_str) > 9:
             data_str = f"{weight_val:+9.1f}" # Fallback for larger numbers
        
        # Unit formatting (3 chars)
        unit_str = self.unit.rjust(3) # " kg" or "  g"
        if self.unit == "kg":
            unit_str = "kg " # A&D manual says "kg_" (space at end?) or "kg"
            # Manual says: "kg_" : kilogram. Let's try "kg "
        elif self.unit == "g":
            unit_str = " g " # " g_"

        response = f"{header},{data_str}{unit_str}"
        return response.encode('ascii') + self.terminator

    def _build_ack(self) -> bytes:
        # <AK> (06h)
        return b'\x06' + self.terminator

    def _build_error(self, error_code: str) -> bytes:
        # EC, Exx
        return f"EC,{error_code}".encode('ascii') + self.terminator

    def _get_current_weight_data(self) -> bytes:
        return self._build_weight_response()
