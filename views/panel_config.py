import tkinter as tk
from tkinter import ttk
from controllers.ids_controller import IDSController

class PanelConfig(tk.Frame):
    def __init__(self, parent, controller: IDSController):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()

    def create_widgets(self):
        # Custom "menu" using buttons
        menu_frame = tk.Frame(self)
        menu_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

        style = ttk.Style()
        style.configure("Custom.TButton", background="#f0f0f0", relief="flat", padding=(10,5))

        ttk.Button(menu_frame, text="Change Update Interval", style="Custom.TButton", command=self.show_change_interval).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Manage Snort Rules", style="Custom.TButton", command=self.manage_snort_rules).pack(side=tk.LEFT, padx=5)
        ttk.Button(menu_frame, text="Manage UFW Rules", style="Custom.TButton", command=self.manage_ufw_rules).pack(side=tk.LEFT, padx=5)

        # Create the interval frame and text widget, but initially hidden
        self.interval_frame = tk.Frame(self)
        self.interval_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        
        update_interval_label = ttk.Label(self.interval_frame, text="Khoảng thời gian cập nhật (ms):")
        update_interval_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.update_interval_entry = ttk.Entry(self.interval_frame)
        self.update_interval_entry.grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)
        self.update_interval_entry.insert(0, str(self.controller.config["update_interval"]))

        max_items_label = ttk.Label(self.interval_frame, text="Số mục tối đa trong Listbox:")
        max_items_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5) #Corrected grid call

        self.max_items_entry = ttk.Entry(self.interval_frame)
        self.max_items_entry.grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)  #Corrected grid call
        self.max_items_entry.insert(0, str(self.controller.config["max_listbox_items"]))
        
        save_button = ttk.Button(self.interval_frame, text="Lưu", command=self.save_config)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)  #Changed row for better spacing

        self.interval_frame.grid_remove()

        # Create the snort rule frame and text widget, but initially hidden
        self.changing_snort_frame = tk.Frame(self)



    def show_change_interval(self):
        self.interval_frame.grid() #Show the frame
        print("Changing update interval...")

    def hide_change_interval(self):
        self.interval_frame.grid_remove()

    def change_max_items(self):
        print("Changing max listbox items...")

    def manage_snort_rules(self):
        print("Managing Snort rules...")

    def manage_ufw_rules(self):
        print("Managing UFW rules...")
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
