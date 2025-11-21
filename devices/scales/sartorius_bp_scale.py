from .base_scale import BaseScale
import logging

class SartoriusBPScale(BaseScale):
    def __init__(self, name: str, device_id: str):
        super().__init__(name, device_id)
        self.terminator = b'\r\n'
        self.unit = "g" # Default unit

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
        # Sartorius BP Format (16 chars)
        # [Sign(1)][Space/Digit(10)][Unit(3)][CR][LF]
        # Sign: '+', '-', ' '
        # Data: Right aligned, 10 chars
        # Unit: 3 chars
        
        if self.current_weight > 999999: # Overload
            # Special code: "Stat High" or similar?
            # Manual says: "High" for overload
            # Let's output "        High" (12 chars) + Unit? Or just text?
            # Manual: "      High  " (12 chars) ?
            # Let's approximate: "High" usually replaces the number.
            resp_str = "        High   " # 16 chars total?
            # Let's stick to standard format if possible or simple text
            return b"        High   \r\n"

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

        # Construct: Sign + Data + Unit
        # Note: Manual says [Sign(1)][Space/Digit(10)][Unit(3)]
        # Example: "+    123.45 g  "
        
        response = f"{sign}{data_str} {unit_str}" # Added space before unit? Manual: [Unit(3)]
        # Wait, manual example: "+    123.45 g  "
        # Sign(1): "+"
        # Data(10): "    123.45"
        # Unit(3): " g " ??
        # Let's try to match 16 chars length (excluding CR LF)
        
        # Re-check example: "+    123.45 g  " -> 1 + 10 + 1(space?) + 3? = 15?
        # Manual says 16 chars.
        # Maybe Unit is 3 chars, but preceded by space?
        # Let's assume: Sign(1) + Data(10) + Unit(5 including spaces)?
        # Or Sign(1) + Data(11) + Unit(4)?
        
        # Let's follow the structure strictly:
        # [Sign(1)][Data(10)][Unit(3)] = 14 chars? That's short.
        # Maybe Data is 11 or 12?
        # Let's assume 16 chars total.
        # Sign(1) + Data(11) + Unit(4)?
        
        # Let's use a safe formatting:
        # Sign(1) + Data(10) + Space(1) + Unit(3) + Space(1) = 16?
        
        # Let's try: "{sign}{data_str:>10} {unit_str:<3}"
        # + "    123.45" + " " + "g  " = 1 + 10 + 1 + 3 = 15. Still 1 short.
        # Maybe Data is 11 chars?
        
        data_str = f"{weight_val:11.2f}" # 11 chars
        response = f"{sign}{data_str} {unit_str}" # 1+11+1+3 = 16.
        
        return response.encode('ascii') + self.terminator

    def _get_current_weight_data(self) -> bytes:
        return self._build_weight_response()
