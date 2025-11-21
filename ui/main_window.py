import tkinter as tk
from tkinter import ttk
import logging
from core.simulator import Simulator
from devices.scales.base_scale import BaseScale
from ui.device_widgets import ScaleControlWidget

class MainWindow(tk.Tk):
    def __init__(self, simulator: Simulator):
        super().__init__()
        self.simulator = simulator
        self.title("EquipSimulator")
        self.geometry("900x600")
        
        self._setup_ui()
        self._setup_logging()
        self._populate_device_list()

    def _setup_ui(self):
        # Main Layout
        self.main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar (Device List)
        self.sidebar_frame = ttk.Frame(self.main_container, width=250)
        self.main_container.add(self.sidebar_frame, weight=1)
        
        self.device_list_label = ttk.Label(self.sidebar_frame, text="Devices")
        self.device_list_label.pack(pady=5)
        
        self.device_listbox = tk.Listbox(self.sidebar_frame)
        self.device_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.device_listbox.bind('<<ListboxSelect>>', self._on_device_select)

        # Content Area
        self.content_frame = ttk.Frame(self.main_container)
        self.main_container.add(self.content_frame, weight=3)
        
        self.current_widget = None
        self.placeholder_label = ttk.Label(self.content_frame, text="Select a device to configure")
        self.placeholder_label.pack(pady=20)

        # Log Area (Bottom)
        self.bottom_notebook = ttk.Notebook(self)
        self.bottom_notebook.pack(fill=tk.X, side=tk.BOTTOM, padx=5, pady=5)

        # Tab 1: System Logs
        self.log_frame = ttk.Frame(self.bottom_notebook)
        self.bottom_notebook.add(self.log_frame, text="System Logs")
        
        # Debug Checkbox (moved to log frame)
        self.debug_var = tk.BooleanVar(value=False)
        self.debug_check = ttk.Checkbutton(self.log_frame, text="Show Serial Data", variable=self.debug_var, command=self._toggle_debug_mode)
        self.debug_check.pack(anchor=tk.W, padx=5)

        self.log_text = tk.Text(self.log_frame, height=8, state='disabled')
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Tab 2: Comm Monitor
        from .monitor_widget import MonitorWidget
        self.monitor_widget = MonitorWidget(self.bottom_notebook)
        self.bottom_notebook.add(self.monitor_widget, text="Comm Monitor")
        
        # Register monitor
        self.simulator.comm_manager.add_monitor(self.monitor_widget.add_log)

    def _populate_device_list(self):
        for name in self.simulator.devices:
            self.device_listbox.insert(tk.END, name)

    def _on_device_select(self, event):
        selection = self.device_listbox.curselection()
        if not selection:
            return
        
        device_name = self.device_listbox.get(selection[0])
        device = self.simulator.get_device(device_name)
        
        self._show_device_control(device)

    def _show_device_control(self, device):
        # Clear current content
        if self.current_widget:
            self.current_widget.destroy()
        self.placeholder_label.pack_forget()

        # Create new widget based on device type
        if isinstance(device, BaseScale):
            self.current_widget = ScaleControlWidget(self.content_frame, device)
            # Hook up start/stop serial buttons
            self.current_widget.on_start_serial = lambda: self._start_serial_wrapper(device.name, self.current_widget.get_serial_params())
            self.current_widget.on_stop_serial = lambda: self._stop_serial_wrapper(device.name, self.current_widget.get_serial_params())
            self.current_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def _start_serial_wrapper(self, device_name, params):
        success = self.simulator.start_device_comm(
            device_name, 
            params['port'],
            params['baudrate'],
            params['bytesize'],
            params['parity'],
            params['stopbits']
        )
        if success:
            logging.info(f"Started serial comms for {device_name} on {params['port']} with {params}")
        else:
            logging.error(f"Failed to start serial comms for {device_name} on {params['port']}")

    def _stop_serial_wrapper(self, device_name, params):
        port = params['port']
        success = self.simulator.stop_device_comm_by_port(port)
        if success:
            logging.info(f"Stopped serial comms for {device_name} on {port}")
        else:
            logging.error(f"Failed to stop serial comms for {device_name} on {port}")

    def _setup_logging(self):
        # Redirect logging to the text widget
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        
        handler = TextHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _toggle_debug_mode(self):
        level = logging.DEBUG if self.debug_var.get() else logging.INFO
        logging.getLogger().setLevel(level)
        logging.info(f"Log level set to {'DEBUG' if level == logging.DEBUG else 'INFO'}")

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.configure(state='normal')
            self.text_widget.insert(tk.END, msg + '\n')
            self.text_widget.see(tk.END)
            self.text_widget.configure(state='disabled')
        self.text_widget.after(0, append)


