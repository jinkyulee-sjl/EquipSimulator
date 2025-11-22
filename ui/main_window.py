import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
from core.simulator import Simulator
from core.project_manager import ProjectManager
from devices.scales.base_scale import BaseScale
from ui.device_widgets import ScaleControlWidget

class MainWindow(tk.Tk):
    def __init__(self, simulator: Simulator):
        super().__init__()
        self.simulator = simulator
        self.project_manager = ProjectManager()
        self.current_project_file = None
        self.title("EquipSimulator")
        self.geometry("900x600")
        
        self._setup_menu()
        self._setup_ui()
        self._setup_logging()
        self._populate_device_list()

    def _setup_menu(self):
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File Menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        
        file_menu.add_command(label="프로젝트 파일 불러오기", command=self._open_project, accelerator="Ctrl+O")
        file_menu.add_command(label="저장", command=self._save_project, accelerator="Ctrl+S")
        file_menu.add_command(label="다른 이름으로 저장", command=self._save_project_as, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self._exit_app, accelerator="Alt+F4")
        
        # Bind keyboard shortcuts
        self.bind('<Control-o>', lambda e: self._open_project())
        self.bind('<Control-s>', lambda e: self._save_project())
        self.bind('<Control-Shift-S>', lambda e: self._save_project_as())

    def _setup_ui(self):
        # Main Layout
        self.main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Sidebar (Device List)
        self.sidebar_frame = ttk.Frame(self.main_container, width=250)
        self.main_container.add(self.sidebar_frame, weight=1)
        
        # Sidebar Toolbar
        self.sidebar_toolbar = ttk.Frame(self.sidebar_frame)
        self.sidebar_toolbar.pack(fill=tk.X, padx=5, pady=2)
        
        ttk.Label(self.sidebar_toolbar, text="Devices").pack(side=tk.LEFT)
        ttk.Button(self.sidebar_toolbar, text="+", width=3, command=self._show_add_device_dialog).pack(side=tk.RIGHT)
        ttk.Button(self.sidebar_toolbar, text="R", width=3, command=self._show_rename_dialog).pack(side=tk.RIGHT, padx=2)
        
        # Treeview for Device List
        self.device_list = ttk.Treeview(self.sidebar_frame, columns=("Name", "Model"), show="headings")
        self.device_list.heading("Name", text="Device Name")
        self.device_list.heading("Model", text="Model")
        self.device_list.column("Name", width=120)
        self.device_list.column("Model", width=120)
        self.device_list.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.device_list.bind('<<TreeviewSelect>>', self._on_device_select)

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

    def _show_add_device_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Add Device")
        dialog.geometry("300x200")
        
        # Model Selection
        ttk.Label(dialog, text="Model Name:").pack(pady=5)
        type_combo = ttk.Combobox(dialog, values=sorted(list(self.simulator.device_types.keys())), state="readonly")
        type_combo.pack(pady=5)
        if self.simulator.device_types:
            type_combo.current(0)
            
        # Name Input
        ttk.Label(dialog, text="Device Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(pady=5)
        name_entry.insert(0, f"Device_{len(self.simulator.devices)+1}")
        
        def _add():
            type_name = type_combo.get()
            name = name_entry.get()
            if not type_name or not name:
                return
            
            # Generate a simple ID
            dev_id = name.upper().replace(" ", "_")
            
            if self.simulator.create_device(type_name, name, dev_id):
                self._populate_device_list()
                dialog.destroy()
            
        ttk.Button(dialog, text="Add", command=_add, width=20).pack(pady=10, ipady=5)

    def _show_rename_dialog(self):
        selection = self.device_list.selection()
        if not selection:
            return
        
        old_name = self.device_list.item(selection[0])['values'][0]
        device = self.simulator.get_device(old_name)
        old_model = device.model
        
        dialog = tk.Toplevel(self)
        dialog.title("Edit Device")
        dialog.geometry("300x250")
        
        # Model Selection
        ttk.Label(dialog, text="Model Name:").pack(pady=5)
        model_combo = ttk.Combobox(dialog, values=sorted(list(self.simulator.device_types.keys())), state="readonly")
        model_combo.set(old_model)
        model_combo.pack(pady=5)

        # Name Input
        ttk.Label(dialog, text="Device Name:").pack(pady=5)
        name_entry = ttk.Entry(dialog)
        name_entry.pack(pady=5)
        name_entry.insert(0, old_name)
        
        def _update():
            new_name = name_entry.get()
            new_model = model_combo.get()
            if not new_name or not new_model:
                return
            
            if self.simulator.update_device(old_name, new_name, new_model):
                self._populate_device_list()
                # Reselect
                for item in self.device_list.get_children():
                    if self.device_list.item(item)['values'][0] == new_name:
                        self.device_list.selection_set(item)
                        self._on_device_select(None)
                        break
                dialog.destroy()
        
        ttk.Button(dialog, text="Update", command=_update, width=20).pack(pady=10, ipady=5)

    def _populate_device_list(self):
        for item in self.device_list.get_children():
            self.device_list.delete(item)
            
        for name, device in self.simulator.devices.items():
            self.device_list.insert("", tk.END, values=(name, device.model))

    def _on_device_select(self, event):
        selection = self.device_list.selection()
        if not selection:
            return
        
        # Get device name from the first column
        device_name = self.device_list.item(selection[0])['values'][0]
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
            
            # Update monitor filter to show only this device's port
            port = device.connection_settings.get("port", "COM1")
            self.monitor_widget.set_filter(port)

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
            self.simulator.get_device(device_name).connect()
            logging.info(f"Started serial comms for {device_name} on {params['port']} with {params}")
            # Update monitor filter to show this device's communication
            self.monitor_widget.set_filter(params['port'])
        else:
            logging.error(f"Failed to start serial comms for {device_name} on {params['port']}")

    def _stop_serial_wrapper(self, device_name, params):
        port = params['port']
        success = self.simulator.stop_device_comm_by_port(port)
        if success:
            self.simulator.get_device(device_name).disconnect()
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

    def _open_project(self):
        """Open a project file"""
        filepath = filedialog.askopenfilename(
            title="프로젝트 파일 불러오기",
            filetypes=[("EquipSimulator Project", "*.ESPJ"), ("All Files", "*.*")]
        )
        
        if filepath:
            # Stop all active communications before loading new project
            self.simulator.comm_manager.stop_all()
            
            # Clear current UI widget
            if self.current_widget:
                self.current_widget.destroy()
                self.current_widget = None
            self.placeholder_label.pack(pady=20)
            
            # Clear monitor
            self.monitor_widget.clear_log()
            self.monitor_widget.set_filter(None)
            
            if self.project_manager.load_project(self.simulator, filepath):
                self.current_project_file = filepath
                self._populate_device_list()
                self._update_title()
                messagebox.showinfo("성공", "프로젝트를 불러왔습니다.")
            else:
                messagebox.showerror("오류", "프로젝트 파일을 불러오는데 실패했습니다.")
    
    def _save_project(self):
        """Save current project"""
        if self.current_project_file:
            if self.project_manager.save_project(self.simulator, self.current_project_file):
                self._update_title()
                messagebox.showinfo("성공", "프로젝트를 저장했습니다.")
            else:
                messagebox.showerror("오류", "프로젝트 저장에 실패했습니다.")
        else:
            self._save_project_as()
    
    def _save_project_as(self):
        """Save project with new filename"""
        filepath = filedialog.asksaveasfilename(
            title="다른 이름으로 저장",
            defaultextension=".ESPJ",
            filetypes=[("EquipSimulator Project", "*.ESPJ"), ("All Files", "*.*")]
        )
        
        if filepath:
            if self.project_manager.save_project(self.simulator, filepath):
                self.current_project_file = filepath
                self._update_title()
                messagebox.showinfo("성공", "프로젝트를 저장했습니다.")
            else:
                messagebox.showerror("오류", "프로젝트 저장에 실패했습니다.")
    
    def _exit_app(self):
        """Exit application"""
        if messagebox.askokcancel("종료", "프로그램을 종료하시겠습니까?"):
            self.simulator.comm_manager.stop_all()
            self.destroy()
    
    def _update_title(self):
        """Update window title with current project filename"""
        if self.current_project_file:
            import os
            filename = os.path.basename(self.current_project_file)
            self.title(f"EquipSimulator - {filename}")
        else:
            self.title("EquipSimulator")

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
