import tkinter as tk
from tkinter import ttk
from views.panel_status import PanelStatus
from views.panel_logs import PanelLogs
from views.panel_threats import PanelThreats
from views.panel_config import PanelConfig
from views.panel_dashboard import PanelDashboard # Import PanelDashboard
from config.settings import Settings

class MainWindow:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title(Settings.APP_TITLE)
        self.root.geometry(f"{Settings.APP_WIDTH}x{Settings.APP_HEIGHT}")
        self.create_widgets()
        self.data_manager = self.controller.data_manager
        
        self.data_manager.root = self.root # set giá trị root cho datamanager để chạy hàm after
        self.data_manager.update_interval = self.data_manager._config.get("update_interval", 60) * 1000  # milliseconds

        # Gọi hàm update_alerts_from_file() định kỳ
        self.after_id = self.root.after(self.data_manager.update_interval, self.update_alerts_from_file)
        
    def update_alerts_from_file(self):
        """Callback function for updating alerts."""
        self.data_manager.update_alerts_from_file()  # Call update method in DataManager
        self.after_id = self.root.after(self.data_manager.update_interval, self.update_alerts_from_file)


    def __del__(self):
        """Hủy bỏ lịch cập nhật khi đóng cửa sổ."""
        if hasattr(self, 'after_id'):
            self.root.after_cancel(self.after_id)

    def create_widgets(self):
        """Tạo các widget cho cửa sổ chính."""
        
        # Configure style
        style = ttk.Style()
        style.theme_use("clam")  # Use any preferred theme
        style.configure("TNotebook.Tab", padding=(20, 10), font=("Helvetica", 12))
        style.configure("TButton", padding=(10, 5), font=("Helvetica", 10))
        
        # Initialize notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(expand=True, fill="both")

        self.frames = {} # Dictionary để lưu trữ các frame/panel

        # Tạo các panel và thêm chúng vào notebook
        panel_dashboard = PanelDashboard(self.notebook, self.controller)
        self.notebook.add(panel_dashboard, text="Dashboard")
        self.frames["dashboard"] = panel_dashboard

        panel_status = PanelStatus(self.notebook, self.controller)
        self.notebook.add(panel_status, text="Status")
        self.frames["status"] = panel_status

        panel_logs = PanelLogs(self.notebook, self.controller)
        self.notebook.add(panel_logs, text="Logs")
        self.frames["logs"] = panel_logs

        panel_threats = PanelThreats(self.notebook, self.controller)
        self.notebook.add(panel_threats, text="Threats")
        self.frames["threats"] = panel_threats

        panel_config = PanelConfig(self.notebook, self.controller)
        self.notebook.add(panel_config, text="Config")
        self.frames["config"] = panel_config



    def show_frame(self, frame_name):
        """Hiển thị frame/panel theo tên."""
        frame = self.frames.get(frame_name)
        if frame:
            self.notebook.select(frame)

    def run(self):
        """Chạy ứng dụng."""
        self.root.mainloop()