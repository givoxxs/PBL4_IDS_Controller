import tkinter as tk
from tkinter import ttk

class PanelConfig(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # ... (Thêm các widget cho phần cấu hình)