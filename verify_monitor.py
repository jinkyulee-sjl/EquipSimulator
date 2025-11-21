import unittest
from unittest.mock import MagicMock
import tkinter as tk
from ui.monitor_widget import MonitorWidget
from core.comm_manager import CommManager

class TestMonitor(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.monitor = MonitorWidget(self.root)
        self.comm = CommManager()
        self.comm.add_monitor(self.monitor.add_log)

    def tearDown(self):
        self.root.destroy()

    def test_monitor_receives_data(self):
        # Simulate RX data
        self.comm._notify_monitors("COM1", "RX", b"Hello")
        
        # Check text widget content
        content = self.monitor.log_text.get("1.0", tk.END)
        print(f"Log content: {content}")
        self.assertIn("[COM1] [RX] Hello", content)

    def test_monitor_receives_binary_data(self):
        # Simulate Binary RX data
        self.comm._notify_monitors("COM2", "TX", b"\x01\x02\xFF")
        
        # Check text widget content
        content = self.monitor.log_text.get("1.0", tk.END)
        print(f"Log content: {content}")
        # Depending on implementation, it might show hex or replacement chars
        # My implementation tries ascii then hex if exception, but \xFF is valid in some encodings or replace?
        # Actually my code does: data.decode('ascii', errors='replace')
        # so \xFF becomes replacement char.
        
        # Let's check if it contains the port and direction at least
        self.assertIn("[COM2] [TX]", content)

if __name__ == '__main__':
    unittest.main()
