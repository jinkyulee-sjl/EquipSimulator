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
        self._current_command_mode = "Simple"
        self._use_bcc = True

    @property
    def available_formats(self):
        return ["Format 1", "Format 2"] # 18 bytes, 22 bytes

    @property
    def available_command_modes(self):
        return ["Simple", "Complex"]

    def set_format(self, format_name: str):
        if format_name in self.available_formats:
            self._current_format = format_name
            super().set_format(format_name)
        else:
            self.logger.warning(f"Invalid format: {format_name}")

    def set_command_mode(self, mode: str):
        if mode in self.available_command_modes:
            self._current_command_mode = mode
            self.logger.info(f"Command mode set to {mode}")

    def set_use_bcc(self, use_bcc: bool):
        self._use_bcc = use_bcc
        self.logger.info(f"Use BCC set to {use_bcc}")

    def process_command(self, command: bytes) -> bytes:
        """
        Handle CAS NT-301A commands.
        Supports Simple Command Mode (F33=5) and Complex Command Mode (F33=1)
        """
        if self._current_command_mode == "Simple":
            return self._process_simple_command(command)
        elif self._current_command_mode == "Complex":
            return self._process_complex_command(command)
        return None

    def _process_simple_command(self, command: bytes) -> bytes:
        try:
            cmd_str = command.decode('ascii', errors='ignore').strip()
        except:
            return None

        self.logger.debug(f"Received Simple command: {cmd_str}")

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

    def _process_complex_command(self, command: bytes) -> bytes:
        # Complex Mode: [STX][ID(2)][COMMAND(4)][BCC(2)][ETX]
        # STX=0x02, ETX=0x03
        if len(command) < 8: # Min length without BCC? STX+ID+CMD+ETX = 1+2+4+1 = 8
            return None
            
        if command[0] != 0x02 or command[-1] != 0x03:
            return None

        try:
            # Extract parts
            # ID: bytes 1-3
            dev_id = command[1:3].decode('ascii')
            
            if dev_id != self.device_id_str:
                return None

            # Command: bytes 3-7
            cmd_name = command[3:7].decode('ascii')
            
            # BCC Check
            if self._use_bcc:
                # Packet should be longer: STX+ID+CMD+BCC+ETX = 1+2+4+2+1 = 10
                if len(command) < 10:
                    return None
                
                received_bcc = command[7:9].decode('ascii')
                # Calculate BCC: XOR from ID to Command (inclusive)
                # Protocol usually says XOR of all characters after STX up to ETX (excluding STX/ETX)?
                # Or XOR of ID + Command?
                # Standard CAS BCC: XOR of all bytes between STX and BCC.
                # i.e. ID(2) + Command(4)
                data_to_check = command[1:7]
                calculated_bcc_val = 0
                for b in data_to_check:
                    calculated_bcc_val ^= b
                calculated_bcc_hex = f"{calculated_bcc_val:02X}"
                
                if received_bcc != calculated_bcc_hex:
                    self.logger.warning(f"BCC Mismatch: Recv {received_bcc}, Calc {calculated_bcc_hex}")
                    return None # Ignore or send NAK? Protocol doesn't specify NAK.

            # Process Command
            # Commands are 4 characters: RCWT, WZER, WTAR
            
            # Let's re-read the command part from the buffer based on length
            # If BCC is used, end is -3. If not, end is -1.
            end_idx = -3 if self._use_bcc else -1
            cmd_part = command[3:end_idx]
            cmd_str = cmd_part.decode('ascii')
            
            if cmd_str.startswith('RCWT'): # Current Weight Request
                return self._build_complex_response(cmd_str, is_weight=True)
            elif cmd_str.startswith('WZER'): # Zero
                self.set_weight(0.0)
                self.tare_weight = 0.0
                return self._build_complex_response(cmd_str, ack=True)
            elif cmd_str.startswith('WTAR'): # Tare
                self.tare_weight = self.current_weight
                return self._build_complex_response(cmd_str, ack=True)
            elif cmd_str.startswith('WTRS'): # Tare Reset
                self.tare_weight = 0.0
                return self._build_complex_response(cmd_str, ack=True)
                
        except Exception as e:
            self.logger.error(f"Error processing complex command: {e}")
            return None
            
        return None

    def _build_complex_response(self, cmd_name: str, is_weight: bool = False, ack: bool = False) -> bytes:
        # Response: [STX][ID(2)][COMMAND(4)][ACK][BCC(2)][ETX]
        # For RCWT (Weight Request):
        # [STX(1)][ID(2)][CMD(4)][STAT1(2)][STAT2(2)][SIGN(1)][DATA(7)][UNIT(2)][ACK(1)][ETX(1)]
        # Total 23 bytes (without BCC)
        
        # Construct payload components
        id_str = self.device_id_str # 2 chars
        cmd_str = cmd_name[:4] # 4 chars
        
        payload = ""
        
        if is_weight:
            # Status 1
            if self.current_weight > 999999:
                stat1 = "OL"
            elif self.is_stable:
                stat1 = "ST"
            else:
                stat1 = "US"
                
            # Status 2
            if self.tare_weight > 0:
                stat2 = "NT"
                val = self.current_weight - self.tare_weight
            else:
                stat2 = "GS"
                val = self.current_weight
                
            # Sign
            sign = "+" if val >= 0 else "-"
            
            # Data (7 chars including dot)
            # e.g. "00123.4"
            abs_val = abs(val)
            data_str = f"{abs_val:07.1f}" # 7 chars, 1 decimal
            if len(data_str) > 7:
                 data_str = f"{abs_val:7.0f}" # Fallback
            
            # Unit (2 chars)
            unit_str = self.unit[:2].ljust(2)
            
            # Combine for payload (excluding STX, ACK, ETX for now)
            # Note: The user spec has ACK at the end.
            # ID(2) + CMD(4) + STAT1(2) + STAT2(2) + SIGN(1) + DATA(7) + UNIT(2)
            payload = f"{id_str}{cmd_str}{stat1}{stat2}{sign}{data_str}{unit_str}"
            
        else:
            # Standard ACK response for other commands?
            # [STX][ID(2)][COMMAND(4)][ACK][BCC(2)][ETX]
            # Payload for BCC calc usually includes ID+CMD+ACK?
            # Let's assume standard structure for non-weight commands
            payload = f"{id_str}{cmd_str}"

        # Build bytes
        response_bytes = bytearray()
        response_bytes.append(0x02) # STX
        response_bytes.extend(payload.encode('ascii'))
        
        response_bytes.append(0x06) # ACK (Always included per spec for RCWT, and likely others)
            
        # Calculate BCC
        if self._use_bcc:
            bcc_val = 0
            # XOR from ID (index 1) to end of payload/ACK
            for b in response_bytes[1:]:
                bcc_val ^= b
            
            bcc_hex = f"{bcc_val:02X}".encode('ascii')
            response_bytes.extend(bcc_hex)
            
        response_bytes.append(0x03) # ETX
        
        return bytes(response_bytes)

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
