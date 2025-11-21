import threading
import time
import socket
import serial
import logging
from typing import Dict, Optional, Callable

class CommManager:
    def __init__(self):
        self.serial_ports: Dict[str, serial.Serial] = {}
        self.tcp_servers: Dict[int, socket.socket] = {}
        self.running = False
        self.logger = logging.getLogger("CommManager")
        self._monitors: List[Callable[[str, str, bytes], None]] = []

    def add_monitor(self, callback: Callable[[str, str, bytes], None]):
        """
        Add a monitor callback.
        Callback signature: (port_name, direction, data)
        direction is 'RX' or 'TX'
        """
        if callback not in self._monitors:
            self._monitors.append(callback)

    def remove_monitor(self, callback: Callable[[str, str, bytes], None]):
        if callback in self._monitors:
            self._monitors.remove(callback)

    def _notify_monitors(self, port: str, direction: str, data: bytes):
        for monitor in self._monitors:
            try:
                monitor(port, direction, data)
            except Exception as e:
                self.logger.error(f"Error in monitor callback: {e}")

    def start_serial(self, port: str, baudrate: int, bytesize: int, parity: str, stopbits: float, callback: Callable[[bytes], bytes]):
        """
        Start listening on a serial port.
        :param port: COM port name (e.g., 'COM1')
        :param baudrate: Baud rate
        :param bytesize: Number of data bits
        :param parity: Parity check
        :param stopbits: Number of stop bits
        :param callback: Function to call when data is received. Should return response bytes.
        """
        try:
            ser = serial.Serial(
                port=port,
                baudrate=baudrate,
                bytesize=bytesize,
                parity=parity,
                stopbits=stopbits,
                timeout=0.1,
                dsrdtr=False
            )
            ser.dtr = True
            ser.rts = True
            self.serial_ports[port] = ser
            self.logger.info(f"Opened serial port {port} at {baudrate}, {bytesize} data bits, {parity} parity, {stopbits} stop bits")
            
            thread = threading.Thread(target=self._serial_loop, args=(port, callback), daemon=True)
            thread.start()
            return True
        except Exception as e:
            self.logger.error(f"Failed to open serial port {port}: {e}")
            return False

    def _serial_loop(self, port: str, callback: Callable[[bytes], bytes]):
        ser = self.serial_ports.get(port)
        while ser and ser.is_open:
            try:
                if ser.in_waiting > 0:
                    data = ser.read(ser.in_waiting)
                    if data:
                        self.logger.debug(f"[{port}] RX: {data}")
                        self._notify_monitors(port, "RX", data)
                        
                        response = callback(data)
                        if response:
                            ser.write(response)
                            self.logger.debug(f"[{port}] TX: {response}")
                            self._notify_monitors(port, "TX", response)
            except Exception as e:
                self.logger.error(f"Error in serial loop {port}: {e}")
                # Don't break the loop on transient errors, just log and continue
                # break
            
            time.sleep(0.01)

    def write(self, port: str, data: bytes):
        """
        Send data to a serial port directly (unsolicited).
        """
        ser = self.serial_ports.get(port)
        if ser and ser.is_open:
            try:
                ser.write(data)
                self.logger.debug(f"[{port}] TX (Stream): {data}")
                self._notify_monitors(port, "TX", data)
                return True
            except Exception as e:
                self.logger.error(f"Error writing to {port}: {e}")
        return False

    def stop_serial(self, port: str):
        """
        Stop listening on a specific serial port.
        """
        ser = self.serial_ports.get(port)
        if ser and ser.is_open:
            try:
                ser.close()
                self.logger.info(f"Closed serial port {port}")
            except Exception as e:
                self.logger.error(f"Error closing serial port {port}: {e}")
            finally:
                del self.serial_ports[port]
            return True
        return False

    def stop_all(self):
        self.running = False
        for port, ser in self.serial_ports.items():
            if ser.is_open:
                ser.close()
        self.serial_ports.clear()
        # TODO: Close TCP servers
