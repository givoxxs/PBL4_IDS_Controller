import tkinter as tk
from tkinter import ttk

class PanelStatus(tk.Frame):
    def __init__(self, parent, controller):
         super().__init__(parent)
         self.controller = controller
         # ... (Thêm các widget để hiển thị trạng thái hệ thống)
         # Ví dụ: label hiển thị trạng thái Snort, UFW, ...