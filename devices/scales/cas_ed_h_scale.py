from .base_scale import BaseScale
import logging

class CasEdHScale(BaseScale):
    def __init__(self, name: str, device_id: str):
        super().__init__(name, device_id)
        self.terminator = b'\r\n'
        self.unit = "kg"
        self.tare_weight = 0.0
        # Default settings
        self.connection_settings.update({
            "baudrate": 9600,
            "bytesize": 8,
            "parity": "N",
            "stopbits": 1
        })

    def process_command(self, command: bytes) -> bytes:
        """
        Handle CAS ED-H / EC-D commands.
        """
        try:
            cmd_str = command.decode('ascii', errors='ignore').strip()
        except:
            return None

        self.logger.debug(f"Received command: {cmd_str}")

        if not cmd_str:
            return None

        # Command mapping based on protocol
        # P or p: Print (Send current weight)
        if cmd_str.upper() == 'P':
            return self._build_stream_packet()
        
        # Z or z: Zero
        elif cmd_str.upper() == 'Z':
            self.set_weight(0.0)
            self.tare_weight = 0.0
            return None # No response specified for Z command in manual usually, or just silent
            
        # T or t: Tare (or C/c)
        elif cmd_str.upper() in ['T', 'C']:
            self.tare_weight = self.current_weight
            return None
            
        # L or l: Load 0? (Manual says "L: Load 0") - treating as Zero for now if ambiguous, or ignore
        elif cmd_str.upper() == 'L':
            self.set_weight(0.0)
            self.tare_weight = 0.0
            return None

        # R or r: Gross/Net switch - Internal state change only, affects display/stream
        # For simulator, we might just toggle a flag if we want to simulate display state.
        # For now, we'll just ignore or log.
        
        # U or u: Unit switch
        
        return None

    def _build_stream_packet(self) -> bytes:
        """
        Builds the 22-byte stream packet.
        Format: [HEAD1(2)][,][HEAD2(2)][,][DATA(8)][UNIT(4)][CR][LF]
        """
        # Header 1
        if self.current_weight > 999999: # Simple overload check
            head1 = "OL"
        elif self.is_stable:
            head1 = "ST"
        else:
            head1 = "US"

        # Header 2 & Value calculation
        # If tare is set, we might be in Net mode. 
        # The protocol says "NT" for Net, "GS" for Gross.
        # Let's assume if tare > 0, we send Net.
        if self.tare_weight > 0:
            head2 = "NT"
            val = self.current_weight - self.tare_weight
        else:
            head2 = "GS"
            val = self.current_weight

        # Data: 8 chars, right aligned.
        # e.g. "+  100.0" or "-   10.5"
        # 2D(Hex)='-', 20(Hex)=' ', 2E(Hex)='.'
        # Python f-string formatting
        # We need to handle sign manually to match exact spacing if needed, 
        # but standard float formatting usually works.
        # Manual example: "+  0.876" (8 chars)
        
        # Create string with sign
        if val >= 0:
            sign = "+"
            val_abs = val
        else:
            sign = "-"
            val_abs = abs(val)
            
        # Format value to string first, e.g. "0.876" or "100.0"
        # Let's assume 1 decimal place for generic usage, or based on value
        val_str = f"{val_abs:.1f}" # "100.0"
        
        # Total length of data part must be 8.
        # [Sign][Space...][Value]
        # Example: "+  100.0" -> Sign(1) + Spaces(2) + Value(5) = 8
        
        # Remaining space for padding
        # 8 - 1(sign) - len(val_str)
        padding_len = 8 - 1 - len(val_str)
        if padding_len < 0:
            # Overflow or too large, just clamp or show what fits?
            # Or maybe reduce precision?
            # For simulator, let's just fit it.
            data_field = f"{sign}{val_str}"
            if len(data_field) < 8:
                data_field = f"{sign}{' '* (8 - len(data_field))}{val_str}"
        else:
            data_field = f"{sign}{' ' * padding_len}{val_str}"

        # Unit: 4 bytes
        # g: " g  " (20 67 20 20)
        # kg: " kg " (20 6B 67 20)
        # Protocol specifies unit starts with space (0x20)
        unit_field = f" {self.unit}".ljust(4)

        # Assemble
        # [HEAD1],[HEAD2],[DATA][UNIT]
        packet = f"{head1},{head2},{data_field}{unit_field}"
        
        return packet.encode('ascii') + self.terminator

    def _get_current_weight_data(self) -> bytes:
        # Used for stream mode
        return self._build_stream_packet()
