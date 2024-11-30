import tkinter as tk
from tkinter import ttk
from utils.check_services_status import check_snort_status, check_UFW_status
from matplotlib import rcParams

class PanelStatus(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        rcParams.update({'figure.autolayout': True})
        self.create_widgets()
        self.update_data()        

    def create_widgets(self):
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        
        snort_UFW_frame = ttk.Frame(self)

        snort_UFW_label = ttk.LabelFrame(self)
        snort_UFW_label.grid()

        snort_frame = ttk.LabelFrame(self, text="Snort Status",  width=10, height=10)
        snort_frame.grid(row=0, column=0,padx=10, pady=7, sticky="nsew")

        UFW_frame = ttk.LabelFrame(self, text="UFW Status")
        UFW_frame.grid(row=0, column=1, padx=10, pady=7, sticky="nsew")

        # Refresh Button
        refresh_button = ttk.Button(self, text="Refresh", command = self.refresh_data)
        refresh_button.grid(row=2, column=0, columnspan=3, pady=(10, 0))

        self.snort_status_text = tk.Text(snort_frame, wrap=tk.WORD, height=6)
        self.snort_status_text.pack(fill=tk.BOTH, expand=True)

        self.UFW_status_text = tk.Text(UFW_frame, wrap=tk.WORD, height=6)
        self.UFW_status_text.pack(fill=tk.BOTH, expand=True)

    def update_data(self):
        self.check_status()  
        

    def check_status(self):
        ufw_status = check_UFW_status()
        snort_status = check_snort_status()
        self.snort_status_text.delete("1.0", tk.END)
        self.UFW_status_text.delete("1.0", tk.END)
        self.snort_status_text.insert(tk.END, f"Snort Status: {snort_status} \n")
        self.UFW_status_text.insert(tk.END, f"UFW Status: {ufw_status}")
    def refresh_data(self):
        self.snort_status_text.delete("1.0", tk.END)
        self.UFW_status_text.delete("1.0", tk.END)
        self.check_status()
        
