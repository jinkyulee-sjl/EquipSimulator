import tkinter as tk
from tkinter import ttk
import datetime

class MonitorWidget(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self._setup_ui()
        self.max_lines = 1000

    def _setup_ui(self):
        # Toolbar
        self.toolbar = ttk.Frame(self)
        self.toolbar.pack(fill=tk.X, padx=5, pady=2)

        self.clear_btn = ttk.Button(self.toolbar, text="Clear", command=self.clear_log)
        self.clear_btn.pack(side=tk.LEFT)

        self.autoscroll_var = tk.BooleanVar(value=True)
        self.autoscroll_check = ttk.Checkbutton(self.toolbar, text="Auto Scroll", variable=self.autoscroll_var)
        self.autoscroll_check.pack(side=tk.LEFT, padx=10)

        # Log Area
        self.log_text = tk.Text(self, height=10, state='disabled', font=("Consolas", 9))
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Tags for coloring
        self.log_text.tag_config("RX", foreground="green")
        self.log_text.tag_config("TX", foreground="blue")
        self.log_text.tag_config("ERROR", foreground="red")

    def add_log(self, port: str, direction: str, data: bytes):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        # Format data
        try:
            # Try to decode as ASCII for display, replace non-printable
            text_data = data.decode('ascii', errors='replace')
            # Also show hex if needed, but for now let's stick to a clean format
            # Maybe "HEX [ASCII]"
            hex_data = data.hex().upper()
            display_text = f"[{timestamp}] [{port}] [{direction}] {text_data} <{hex_data}>\n"
        except Exception:
            display_text = f"[{timestamp}] [{port}] [{direction}] <BINARY: {data.hex().upper()}>\n"

        def _update_ui():
            self.log_text.configure(state='normal')
            self.log_text.insert(tk.END, display_text, direction)
            
            # Limit lines
            if float(self.log_text.index('end-1c')) > self.max_lines:
                self.log_text.delete('1.0', '2.0')

            if self.autoscroll_var.get():
                self.log_text.see(tk.END)
                
            self.log_text.configure(state='disabled')

        self.after(0, _update_ui)

    def clear_log(self):
        self.log_text.configure(state='normal')
        self.log_text.delete('1.0', tk.END)
        self.log_text.configure(state='disabled')
