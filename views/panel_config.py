import tkinter as tk
from tkinter import ttk, messagebox
import json
from config.settings import Settings


class PanelConfig(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.config_file = "config.json"

        # Tải cấu hình từ file hoặc tạo mới nếu không tồn tại
        self.config = self.load_config()

        # Trạng thái chỉnh sửa (ban đầu là False)
        self.edit_mode = False

        # Thêm các widget cho phần cấu hình
        self.create_widgets()
        self.toggle_editable(False)  # Khóa chỉnh sửa ban đầu

    def load_config(self):
        """Tải cấu hình từ file config.json hoặc tạo file nếu không tồn tại."""
        try:
            with open(self.config_file, "r") as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Nếu không tìm thấy file config.json hoặc có lỗi khi đọc, tạo file với dữ liệu mặc định
            config = {
                "sid": 1000016,
                "threshold": 10,
                "update_interval": 60,
                "max_alerts": 5000,
            }
            self.save_config(config)
        return config

    def save_config(self, config):
        """Lưu cấu hình vào file config.json."""
        with open(self.config_file, "w") as f:
            json.dump(config, f, indent=4)

    def create_widgets(self):
        """Tạo các widget cho phần cấu hình."""
        # Cấu hình giao diện
        self.label_update_interval = tk.Label(self, text="Update Interval (seconds):")
        self.label_update_interval.grid(row=0, column=0, sticky="w", padx=10, pady=5)

        self.entry_update_interval = ttk.Entry(self)
        self.entry_update_interval.insert(0, str(self.config["update_interval"]))
        self.entry_update_interval.grid(row=0, column=1, padx=10, pady=5)

        self.label_max_alerts = tk.Label(self, text="Max Alerts to Load:")
        self.label_max_alerts.grid(row=1, column=0, sticky="w", padx=10, pady=5)

        self.entry_max_alerts = ttk.Entry(self)
        self.entry_max_alerts.insert(0, str(self.config["max_alerts"]))
        self.entry_max_alerts.grid(row=1, column=1, padx=10, pady=5)

        self.label_threshold = tk.Label(self, text="Threshold:")
        self.label_threshold.grid(row=2, column=0, sticky="w", padx=10, pady=5)

        self.entry_threshold = ttk.Entry(self)
        self.entry_threshold.insert(0, str(self.config["threshold"]))
        self.entry_threshold.grid(row=2, column=1, padx=10, pady=5)

        # Nút Edit và Save
        self.button_edit = ttk.Button(self, text="Edit", command=self.enable_editing)
        self.button_edit.grid(row=3, column=0, pady=10, padx=5)

        self.button_save = ttk.Button(self, text="Save", command=self.save_changes, state="disabled")
        self.button_save.grid(row=3, column=1, pady=10, padx=5)

    def toggle_editable(self, editable):
        """Khóa hoặc mở khóa chỉnh sửa các entry."""
        state = "normal" if editable else "disabled"
        self.entry_update_interval.config(state=state)
        self.entry_max_alerts.config(state=state)
        self.entry_threshold.config(state=state)

        # Chuyển đổi trạng thái nút
        self.button_edit.config(state="normal" if not editable else "disabled")
        self.button_save.config(state="normal" if editable else "disabled")

    def enable_editing(self):
        """Kích hoạt chế độ chỉnh sửa."""
        self.edit_mode = True
        self.toggle_editable(True)

    def save_changes(self):
        """Lưu thay đổi vào file config.json."""
        try:
            update_interval = int(self.entry_update_interval.get())
            max_alerts = int(self.entry_max_alerts.get())
            threshold = int(self.entry_threshold.get())

            # Cập nhật cấu hình mới
            self.config["update_interval"] = update_interval
            self.config["max_alerts"] = max_alerts
            self.config["threshold"] = threshold

            # Lưu cấu hình mới vào file
            self.save_config(self.config)

            # Tải lại config trong controller (nếu có)
            if hasattr(self.controller, "data_manager"):
                self.controller.data_manager.reload_config()

            # Thông báo đã lưu thành công
            messagebox.showinfo("Success", "Configuration saved successfully!")

            # Khóa chỉnh sửa
            self.edit_mode = False
            self.toggle_editable(False)
        except ValueError:
            messagebox.showerror("Error", "Please enter valid integer values.")
