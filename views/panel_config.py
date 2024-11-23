import json
import tkinter as tk
from tkinter import ttk
from controllers.ids_controller import IDSController

class PanelConfig(tk.Frame):
    def __init__(self, parent, controller: IDSController):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Widgets for configuration
        update_interval_label = ttk.Label(self, text="Khoảng thời gian cập nhật (ms):")
        update_interval_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.update_interval_entry = ttk.Entry(self)
        self.update_interval_entry.grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)
        self.update_interval_entry.insert(0, str(self.controller.config["update_interval"]))

        max_items_label = ttk.Label(self, text="Số mục tối đa trong Listbox:")
        max_items_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.max_items_entry = ttk.Entry(self)
        self.max_items_entry.grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)
        self.max_items_entry.insert(0, str(self.controller.config["max_listbox_items"]))

        save_button = ttk.Button(self, text="Lưu", command=self.save_config)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)


    def save_config(self):
        try:
            self.controller.config["update_interval"] = int(self.update_interval_entry.get())
            self.controller.config["max_listbox_items"] = int(self.max_items_entry.get())
            self.controller.save_config()
            # Optionally trigger a dashboard refresh:
            self.controller.update_dashboard()

        except ValueError:
            print("Invalid input. Please enter numbers only.")
        except Exception as e:
            print(f"Error saving config: {e}")