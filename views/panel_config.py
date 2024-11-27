import tkinter as tk
from tkinter import *
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

        # Create the interval frame
        self.interval_frame = tk.Frame(self)
        self.interval_frame.grid(row=3, column=0, sticky="nsew", padx=10, pady=10)
        
        # Create update interval label & entry
        update_interval_label = ttk.Label(self.interval_frame, text="Update interval (ms): ")
        update_interval_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.update_interval_entry = ttk.Entry(self.interval_frame)
        self.update_interval_entry.grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)
        self.update_interval_entry.insert(0, str(self.controller.config["update_interval"]))

        # Create update max_items label & entry
        max_items_label = ttk.Label(self.interval_frame, text="Max listbox items: ")
        max_items_label.grid(row=1, column=0, sticky=tk.W, padx=5, pady=5) 
        self.max_items_entry = ttk.Entry(self.interval_frame)
        self.max_items_entry.grid(row=1, column=1, sticky=tk.E, padx=5, pady=5)  
        self.max_items_entry.insert(0, str(self.controller.config["max_listbox_items"]))
        
        #Create save button
        save_button = ttk.Button(self.interval_frame, text="Save", command=self.save_config)
        save_button.grid(row=2, column=0, columnspan=2, pady=10)  

        #hide interval_frame at initialization
        self.interval_frame.grid_remove()
        
        # Create the snort rule frame and text widget
        self.changing_snort_frame = tk.Frame(self)
        self.changing_snort_frame.grid(row=3, column=2, sticky="nsew", padx=50, pady=70)

        # Create changing_snort label & entry
        changing_snort_label = ttk.Label(self.changing_snort_frame, text="Update your snort rules: ")
        changing_snort_label.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.changing_snort_entry = ttk.Entry(self.changing_snort_frame)
        self.changing_snort_entry.grid(row=0, column=1, sticky=tk.E, padx=5, pady=5)
        # self.changing_snort_entry.insert(0, str(self.controller.config["update_snort_rules"]))

        #hide changing_snort_frame at initialization
        self.changing_snort_frame.grid_remove()

    def show_change_interval(self):
        self.changing_snort_frame.grid_remove()
        self.interval_frame.grid() #Show the frame
        print("Changing update interval...")

    def manage_snort_rules(self):
        #remove other frame
        self.interval_frame.grid_remove()

        #Show the frame
        self.changing_snort_frame.grid()
        print("Managing Snort rules...")
    def create_snort_rules(self):
        pass

    def manage_ufw_rules(self):
        print("Managing UFW rules...")

    def create_ufw_rule(self):
        pass

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
