import tkinter as tk
from tkinter import ttk
from devices.scales.base_scale import BaseScale

class ScaleControlWidget(ttk.Frame):
    def __init__(self, parent, scale: BaseScale):
        super().__init__(parent)
        self.scale = scale
        self._setup_ui()

    def _setup_ui(self):
        # Title
        ttk.Label(self, text=f"Control: {self.scale.name}", font=("Arial", 12, "bold")).pack(pady=10)

        # Weight Control
        weight_frame = ttk.LabelFrame(self, text="Weight Simulation")
        weight_frame.pack(fill=tk.X, padx=5, pady=5)

        self.weight_var = tk.DoubleVar(value=self.scale.current_weight)
        
        # Slider
        ttk.Scale(weight_frame, from_=0, to=1000, variable=self.weight_var, command=self._on_weight_change).pack(fill=tk.X, padx=5, pady=5)
        
        # Entry
        entry_frame = ttk.Frame(weight_frame)
        entry_frame.pack(fill=tk.X, padx=5)
        ttk.Label(entry_frame, text="Value:").pack(side=tk.LEFT)
        ttk.Entry(entry_frame, textvariable=self.weight_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(entry_frame, text="Set", command=self._on_weight_change).pack(side=tk.LEFT)

        # Stability Control
        self.stable_var = tk.BooleanVar(value=self.scale.is_stable)
        ttk.Checkbutton(weight_frame, text="Stable", variable=self.stable_var, command=self._on_stability_change).pack(anchor=tk.W, padx=5, pady=5)

        # Format Selection (if supported)
        if self.scale.available_formats:
            format_frame = ttk.LabelFrame(self, text="Data Format & Mode")
            format_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Format
            ttk.Label(format_frame, text="Format:").pack(side=tk.LEFT, padx=5)
            self.format_combo = ttk.Combobox(format_frame, values=self.scale.available_formats, state="readonly", width=15)
            if self.scale.available_formats:
                self.format_combo.current(0)
            self.format_combo.pack(side=tk.LEFT, padx=5, pady=5)
            self.format_combo.bind("<<ComboboxSelected>>", self._on_format_change)

            # Print Mode
            ttk.Label(format_frame, text="Mode:").pack(side=tk.LEFT, padx=5)
            self.mode_combo = ttk.Combobox(format_frame, values=["Command", "Stream"], state="readonly", width=10)
            self.mode_combo.set(self.scale.print_mode)
            self.mode_combo.pack(side=tk.LEFT, padx=5, pady=5)
            self.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_change)

        # Connection Info
        conn_frame = ttk.LabelFrame(self, text="Connection Settings")
        conn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Row 0: Port & Baud
        ttk.Label(conn_frame, text="Port:").grid(row=0, column=0, padx=5, pady=5)
        self.port_entry = ttk.Entry(conn_frame, width=10)
        self.port_entry.insert(0, "COM1")
        self.port_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(conn_frame, text="Baud:").grid(row=0, column=2, padx=5, pady=5)
        self.baud_combo = ttk.Combobox(conn_frame, values=[9600, 19200, 38400, 57600, 115200], width=7)
        self.baud_combo.set(9600)
        self.baud_combo.grid(row=0, column=3, padx=5, pady=5)

        # Row 1: Data, Parity, Stop
        ttk.Label(conn_frame, text="Data:").grid(row=1, column=0, padx=5, pady=5)
        self.data_combo = ttk.Combobox(conn_frame, values=[7, 8], width=3)
        self.data_combo.set(8)
        self.data_combo.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(conn_frame, text="Parity:").grid(row=1, column=2, padx=5, pady=5)
        self.parity_combo = ttk.Combobox(conn_frame, values=["None", "Even", "Odd", "Mark", "Space"], width=5)
        self.parity_combo.set("None")
        self.parity_combo.grid(row=1, column=3, padx=5, pady=5)

        ttk.Label(conn_frame, text="Stop:").grid(row=1, column=4, padx=5, pady=5)
        self.stop_combo = ttk.Combobox(conn_frame, values=[1, 1.5, 2], width=3)
        self.stop_combo.set(1)
        self.stop_combo.grid(row=1, column=5, padx=5, pady=5)
        
        self.start_btn = ttk.Button(conn_frame, text="Start Serial", command=self._start_serial)
        self.start_btn.grid(row=2, column=0, columnspan=3, padx=5, pady=10)
        
        self.stop_btn = ttk.Button(conn_frame, text="Stop Serial", command=self._stop_serial, state="disabled")
        self.stop_btn.grid(row=2, column=3, columnspan=3, padx=5, pady=10)
        
        self.on_start_serial = None
        self.on_stop_serial = None

    def _on_weight_change(self, *args):
        try:
            val = float(self.weight_var.get())
            self.scale.set_weight(val)
        except ValueError:
            pass

    def _on_stability_change(self):
        self.scale.set_stable(self.stable_var.get())

    def _on_format_change(self, event):
        self.scale.set_format(self.format_combo.get())

    def _on_mode_change(self, event):
        self.scale.set_print_mode(self.mode_combo.get())

    def get_serial_params(self):
        parity_map = {"None": 'N', "Even": 'E', "Odd": 'O', "Mark": 'M', "Space": 'S'}
        return {
            "port": self.port_entry.get(),
            "baudrate": int(self.baud_combo.get()),
            "bytesize": int(self.data_combo.get()),
            "parity": parity_map.get(self.parity_combo.get(), 'N'),
            "stopbits": float(self.stop_combo.get())
        }

    def _start_serial(self):
        if self.on_start_serial:
            self.on_start_serial()
            self._set_conn_state("disabled")

    def _stop_serial(self):
        if self.on_stop_serial:
            self.on_stop_serial()
            self._set_conn_state("normal")

    def _set_conn_state(self, state):
        # Toggle buttons
        if state == "disabled":
            self.start_btn.configure(state="disabled")
            self.stop_btn.configure(state="normal")
        else:
            self.start_btn.configure(state="normal")
            self.stop_btn.configure(state="disabled")

        # Toggle inputs
        self.port_entry.configure(state=state)
        self.baud_combo.configure(state=state)
        self.data_combo.configure(state=state)
        self.parity_combo.configure(state=state)
        self.stop_combo.configure(state=state)
