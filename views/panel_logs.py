import tkinter as tk
from tkinter import ttk
from models.alert import Alert


class PanelLogs(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
        self.display_alerts() # Hiển thị alert ban đầu


    def create_widgets(self):
        """Tạo các widget cho Panel Logs."""

        # Tạo Treeview widget
        columns = Alert.get_columns() # Gọi phương thức get_columns()
        self.tree = ttk.Treeview(self, columns=tuple(columns), show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100) # hoặc width theo ý bạn
        self.tree.pack(fill="both", expand=True)



    def display_alerts(self):
        """Hiển thị alerts trong Treeview."""
        alerts = self.controller.get_alerts()  # Lấy dữ liệu từ controller
        for i in self.tree.get_children(): # Xóa dữ liệu cũ (nếu có)
            self.tree.delete(i)

        for alert in alerts:
            self.tree.insert("", tk.END, values=alert.to_tuple())