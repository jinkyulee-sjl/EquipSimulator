from .base_scale import BaseScale
import logging

class CasCI600A(BaseScale):
    def __init__(self, name: str, device_id: str):
        super().__init__(name, device_id)
        self.terminator = b'\r\n'
        self._current_format = "Format 1"
        self.tare_weight = 0.0
        self._buffer = b""

    @property
    def available_formats(self):
        return ["Format 1", "Format 2", "Format 3"]

    def set_format(self, format_name: str):
        if format_name in self.available_formats:
            self._current_format = format_name
            super().set_format(format_name)
        else:
            self.logger.warning(f"Invalid format: {format_name}")

    def process_command(self, command: bytes) -> bytes:
        """
        Handle CAS CI-600A commands.
        Accumulates bytes until terminator is found.
        """
        self._buffer += command
        
        responses = []
        while self.terminator in self._buffer:
            parts = self._buffer.split(self.terminator, 1)
            cmd_bytes = parts[0]
            self._buffer = parts[1]
            
            try:
                cmd_str = cmd_bytes.decode('ascii', errors='ignore').strip()
            except:
                responses.append(b'?' + self.terminator)
                continue

            self.logger.debug(f"Processing command: {cmd_str}")
            
            if len(cmd_str) < 2:
                 continue
            
            cmd = cmd_str[-2:]
            
            if cmd == 'RW':
                responses.append(self._build_weight_response())
            elif cmd == 'MZ':
                self.set_weight(0.0)
                self.tare_weight = 0.0
                responses.append(self._build_simple_response(cmd_str))
            elif cmd == 'MT':
                self.tare_weight = self.current_weight
                responses.append(self._build_simple_response(cmd_str))
            else:
                responses.append(b'?' + self.terminator)
                
        return b''.join(responses) if responses else None

    def _build_simple_response(self, original_cmd: str) -> bytes:
        # Echo back the command as per protocol for MZ/MT
        return original_cmd.encode('ascii') + self.terminator

    def _build_weight_response(self) -> bytes:
        gross_weight = self.current_weight
        net_weight = gross_weight - self.tare_weight
        
        # Status
        # US: Unstable, ST: Stable, OL: Overload
        status = "ST" if self.is_stable else "US"
        if gross_weight > 999999: # Simple overload check
            status = "OL"
            
        # Weight Type
        # GS: Gross, NT: Net
        weight_type = "NT" if self.tare_weight > 0 else "GS"
        val_to_send = net_weight if weight_type == "NT" else gross_weight
        
        # Format 1 (22 bytes)
        # HDR1(2),.,HDR2(2),.,ID(1),LAMP(1),.,DATA(8),SPACE(1),UNIT(2),CRLF(2)
        if self._current_format == "Format 1":
            # Lamp status byte (simulated)
            # Bt6(Stable), Bt0(Zero)
            lamp = 0
            if self.is_stable: lamp |= (1 << 6)
            if val_to_send == 0: lamp |= (1 << 0)
            if self.tare_weight > 0: lamp |= (1 << 1) # Tare active
            
            lamp_char = chr(0x30 + (lamp & 0x0F)) # Just a placeholder logic to make it printable if needed, or raw byte?
            # Protocol says "1 byte". Usually in ASCII protocols this is a character.
            # Let's use a fixed char '0' for simplicity unless specified.
            lamp_char = '0' 

            # Data: 8 bytes including sign and decimal
            # e.g. " 1234.5 " or "+0123.45"
            # CAS usually uses space padding for numbers.
            data_str = f"{val_to_send:8.1f}"[-8:] 
            
            resp = f"{status}.{weight_type}.1{lamp_char}.{data_str} {self.unit}"
            return resp.encode('ascii') + self.terminator

        # Format 2 (10 bytes)
        # DATA(8),CRLF(2)
        elif self._current_format == "Format 2":
            data_str = f"{val_to_send:8.1f}"[-8:]
            return data_str.encode('ascii') + self.terminator

        # Format 3 (18 bytes)
        # HDR1(2),.,HDR2(2),.,DATA(8),UNIT(2),CRLF(2)
        elif self._current_format == "Format 3":
            data_str = f"{val_to_send:8.1f}"[-8:]
            resp = f"{status}.{weight_type}.{data_str}{self.unit}"
            return resp.encode('ascii') + self.terminator

        return b'?' + self.terminator

    def _get_current_weight_data(self) -> bytes:
        return self._build_weight_response()
