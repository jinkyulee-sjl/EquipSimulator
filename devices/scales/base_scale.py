from core.equipment import Equipment
import threading
import time
from typing import Callable, Optional

class BaseScale(Equipment):
    def __init__(self, name: str, device_id: str):
        super().__init__(name, device_id)
        self.current_weight = 0.0
        self.is_stable = True
        self.unit = "kg"
        self.print_mode = "Command" # Command or Stream
        self.current_format = None
        self.weight_range = {"min": -100, "max": 1000}  # Default slider range
        self._streaming = False
        self._stream_thread: Optional[threading.Thread] = None
        self.on_output: Optional[Callable[[bytes], None]] = None

    def set_weight(self, weight: float):
        self.current_weight = weight
        self.logger.info(f"Weight set to {self.current_weight} {self.unit}")

    def set_stable(self, stable: bool):
        self.is_stable = stable
        self.logger.info(f"Stability set to {self.is_stable}")

    def get_weight_str(self, format_str: str) -> str:
        """
        Helper to format weight string based on protocol requirements.
        """
        return format_str.format(weight=self.current_weight, unit=self.unit)

    @property
    def available_formats(self):
        return []

    def set_format(self, format_name: str):
        self.current_format = format_name
        self.logger.info(f"Format set to {format_name}")

    def set_print_mode(self, mode: str):
        if mode in ["Command", "Stream"]:
            self.print_mode = mode
            self.logger.info(f"Print mode set to {mode}")
            if mode == "Stream":
                self.start_streaming()
            else:
                self.stop_streaming()

    def start_streaming(self):
        if self._streaming:
            return
        self._streaming = True
        self._stream_thread = threading.Thread(target=self._streaming_loop, daemon=True)
        self._stream_thread.start()
        self.logger.info("Started streaming mode")

    def stop_streaming(self):
        self._streaming = False
        if self._stream_thread:
            self._stream_thread.join(timeout=1.0)
            self._stream_thread = None
        self.logger.info("Stopped streaming mode")

    def _streaming_loop(self):
        while self._streaming:
            try:
                if self.on_output:
                    data = self._get_current_weight_data()
                    if data:
                        self.on_output(data)
            except Exception as e:
                self.logger.error(f"Error in streaming loop: {e}")
            time.sleep(0.333) # 3Hz update rate

    def _get_current_weight_data(self) -> bytes:
        """
        Override this in subclasses to return the current weight data packet.
        """
        return None

    def disconnect(self):
        """Override to stop streaming when disconnecting"""
        self.stop_streaming()
        super().disconnect()
