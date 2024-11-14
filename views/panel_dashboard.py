import tkinter as tk
from tkinter import ttk

class PanelDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        # ... (Thêm widget để hiển thị dashboard)