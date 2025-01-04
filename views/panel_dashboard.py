import tkinter as tk
from tkinter import ttk, messagebox
from utils.plotter import Plotter
import matplotlib.pyplot as plt  # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib import rcParams
from controllers.ids_controller import IDSController
import threading
import time

class PanelDashboard(tk.Frame):
    def __init__(self, parent, controller: IDSController):
        super().__init__(parent)
        self.controller = controller
        self.alerts = []
        self.active_popup = None # Track if popup is already open
        # Matplotlib configuration for tighter layout
        rcParams.update({'figure.autolayout': True})  # Adjust layout to prevent labels from overlapping
        self.create_widgets()
        self.update_data()
        
        # Start the threat detection thread
        self.threat_detection_thread = threading.Thread(target=self.detect_high_priority_threats, daemon=True)
        self.threat_detection_thread.start()
        self.stop_thread = False
        

    def create_widgets(self):
        # Frame Summary
        summary_frame = ttk.LabelFrame(self, text="Summary")
        summary_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.total_alerts_label = ttk.Label(summary_frame, text="Total Alerts: 0")
        self.total_alerts_label.pack(pady=5)

        self.unhandled_alerts_label = ttk.Label(summary_frame, text="Unhandled Alerts: 0")
        self.unhandled_alerts_label.pack(pady=5)

        # Frame Charts
        chart_frame = ttk.LabelFrame(self, text="Charts")
        chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Configure chart canvases
        self.fig_time, self.ax_time = plt.subplots()
        self.canvas_time = FigureCanvasTkAgg(self.fig_time, master=chart_frame)
        self.canvas_time.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.fig_ips, self.ax_ips = plt.subplots()
        self.canvas_ips = FigureCanvasTkAgg(self.fig_ips, master=chart_frame)
        self.canvas_ips.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas_ips.get_tk_widget().grid_remove()

        self.fig_types, self.ax_types = plt.subplots()
        self.canvas_types = FigureCanvasTkAgg(self.fig_types, master=chart_frame)
        self.canvas_types.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas_types.get_tk_widget().grid_remove()

        self.fig_rules, self.ax_rules = plt.subplots()
        self.canvas_rules = FigureCanvasTkAgg(self.fig_rules, master=chart_frame)
        self.canvas_rules.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        self.canvas_rules.get_tk_widget().grid_remove()

        # Buttons to switch charts
        chart_buttons_frame = tk.Frame(chart_frame)
        chart_buttons_frame.grid(row=1, column=0, pady=10, sticky="ew")

        self.chart_buttons = {}
        chart_types = ["time", "ips", "types", "rules"]
        for chart_type in chart_types:
            button = tk.Button(
                chart_buttons_frame,
                text=f"Plot {chart_type}",
                command=lambda chart_type=chart_type: self.switch_chart(chart_type),
            )
            button.pack(side=tk.LEFT, padx=5)
            self.chart_buttons[chart_type] = button

        # Frame Top Attacking IPs
        top_ips_frame = ttk.LabelFrame(self, text="Top Attacking IPs")
        top_ips_frame.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="nsew")

        self.top_ips_listbox = tk.Listbox(top_ips_frame)
        self.top_ips_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_ips = ttk.Scrollbar(top_ips_frame, orient=tk.VERTICAL, command=self.top_ips_listbox.yview)
        self.top_ips_listbox.configure(yscrollcommand=scrollbar_ips.set)
        scrollbar_ips.pack(side=tk.RIGHT, fill=tk.Y)

        # Frame Top Alert Rules
        top_rules_frame = ttk.LabelFrame(self, text="Top Alert Rules")
        top_rules_frame.grid(row=1, column=2, padx=10, pady=(10, 0), sticky="nsew")

        self.top_rules_listbox = tk.Listbox(top_rules_frame)
        self.top_rules_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar_rules = ttk.Scrollbar(top_rules_frame, orient=tk.VERTICAL, command=self.top_rules_listbox.yview)
        self.top_rules_listbox.configure(yscrollcommand=scrollbar_rules.set)
        scrollbar_rules.pack(side=tk.RIGHT, fill=tk.Y)

        # Adjust grid weights for responsive layout
        self.columnconfigure(0, weight=2)  # Charts + Summary
        self.columnconfigure(1, weight=1)  # Top IPs/Rules
        self.rowconfigure(0, weight=1)  # Top row
        self.rowconfigure(1, weight=3)  # Bottom row

        # Refresh Button
        refresh_button = ttk.Button(self, text="Refresh", command=self.refresh_data)
        refresh_button.grid(row=2, column=0, columnspan=3, pady=(10, 0))

    def update_data(self):
        """Update data on the dashboard."""
        self.alerts = self.controller.get_alerts()

        # Update alert counts
        self.total_alerts_label.config(text=f"Total Alerts: {len(self.alerts)}")
        unhandled_alerts = [alert for alert in self.alerts if not alert.action_taken]
        self.unhandled_alerts_label.config(text=f"Unhandled Alerts: {len(unhandled_alerts)}")

        # Update charts
        self.plot_alerts_time()
        self.plot_top_ips()
        self.plot_alert_types()
        self.plot_top_rules()

        # Update listboxes
        self.update_top_ips_listbox()
        self.update_top_rules_listbox()

        # Schedule the next update
        self.after(300000, self.update_data)  # Update every 5 minutes
        
    def refresh_data(self):
        """Refresh all data displayed on the dashboard."""
        # Fetch new alerts
        self.alerts = self.controller.get_alerts()

        # Update summary labels
        self.total_alerts_label.config(text=f"Total Alerts: {len(self.alerts)}")
        unhandled_alerts = [alert for alert in self.alerts if not alert.action_taken]
        self.unhandled_alerts_label.config(text=f"Unhandled Alerts: {len(unhandled_alerts)}")

        # Update charts
        self.plot_alerts_time()
        self.plot_top_ips()
        self.plot_alert_types()
        self.plot_top_rules()

        # Update listboxes
        self.update_top_ips_listbox()
        self.update_top_rules_listbox()

        messagebox.showinfo("Refresh Complete", "Dashboard data has been refreshed.")


    def switch_chart(self, chart_type):
        """Switch between charts."""
        for chart, canvas in {
            "time": self.canvas_time,
            "ips": self.canvas_ips,
            "types": self.canvas_types,
            "rules": self.canvas_rules,
        }.items():
            if chart == chart_type:
                canvas.get_tk_widget().grid()
                self.chart_buttons[chart].config(relief=tk.SUNKEN)
            else:
                canvas.get_tk_widget().grid_remove()
                self.chart_buttons[chart].config(relief=tk.RAISED)

    def plot_alerts_time(self):
        Plotter.plot_alerts_over_time(self.ax_time, self.alerts)
        self.fig_time.tight_layout()
        self.canvas_time.draw()

    def plot_top_ips(self):
        Plotter.plot_top_attack_ips(self.ax_ips, self.alerts)
        self.fig_ips.tight_layout()
        self.canvas_ips.draw()

    def plot_alert_types(self):
        Plotter.plot_alert_types(self.ax_types, self.alerts)
        self.fig_types.tight_layout()
        self.canvas_types.draw()

    def plot_top_rules(self):
        Plotter.plot_top_rules(self.ax_rules, self.alerts)
        self.fig_rules.tight_layout()
        self.canvas_rules.draw()

    def update_top_ips_listbox(self):
        top_ips = Plotter.get_top_attack_ips(self.alerts)
        self.top_ips_listbox.delete(0, tk.END)
        for ip, count in top_ips.items():
            self.top_ips_listbox.insert(tk.END, f"{ip}: {count}")

    def update_top_rules_listbox(self):
        top_rules = Plotter.get_top_rules_2(self.alerts)
        self.top_rules_listbox.delete(0, tk.END)
        for rule, count in top_rules.items():
            self.top_rules_listbox.insert(tk.END, f"{rule}: {count}")
            
    def detect_high_priority_threats(self):
        while not self.stop_thread:
            time.sleep(300) # Check for high-priority threats every 5 minutes
            if self.alerts:
                high_priority_alerts = [
                    alert for alert in self.alerts
                    if not alert.action_taken and (alert.occurrence > 20 or alert.priority <= 2)
                ]
                if high_priority_alerts and self.active_popup is None:
                   self.after(0, lambda alerts=high_priority_alerts: self.show_threat_popup(alerts))

    def show_threat_popup(self, alerts):
        self.active_popup = tk.Toplevel(self)
        self.active_popup.title("High-Priority Threats Detected")
        self.active_popup.protocol("WM_DELETE_WINDOW", self.close_popup)

        # Display each threat in the popup
        for alert in alerts:
            alert_frame = ttk.LabelFrame(self.active_popup, text=f"Alert ID: {alert.id}")
            alert_frame.pack(pady=5, padx=10, fill=tk.X)
            
            ttk.Label(alert_frame, text=f"Time: {alert.time}").pack(anchor=tk.W)
            ttk.Label(alert_frame, text=f"Source IP: {alert.source_ip}").pack(anchor=tk.W)
            ttk.Label(alert_frame, text=f"Destination IP: {alert.destination_ip}").pack(anchor=tk.W)
            ttk.Label(alert_frame, text=f"Rule: {alert.rule_name}").pack(anchor=tk.W)
            ttk.Label(alert_frame, text=f"Priority: {alert.priority}").pack(anchor=tk.W)
            ttk.Label(alert_frame, text=f"Occurrence: {alert.occurrence}").pack(anchor=tk.W)
            
            # Create action buttons for each alert
            action_frame = tk.Frame(alert_frame)
            action_frame.pack(fill=tk.X, pady=5, padx=5)
            
            actions = ["Safe", "Limit", "Block", "Ignore"]
            for action in actions:
                button = ttk.Button(action_frame, text=action, command=lambda a=action, alert_id = alert.id: self.handle_action(alert_id, a))
                button.pack(side=tk.LEFT, padx=2)


    def close_popup(self):
         if self.active_popup:
            self.active_popup.destroy()
            self.active_popup = None

    def handle_action(self, alert_id, action):
        """Handles actions taken on a threat (e.g., Safe, Limit, Block, Ignore)."""
        # Logic to handle action
        print(f"Action: {action} for alert ID: {alert_id}")
        self.controller.handle_alert_action(alert_id,action)
        self.close_popup() # Close popup after user has chosen an action
        self.refresh_data()
    
    def on_closing(self):
      self.stop_thread = True
      if self.active_popup:
         self.active_popup.destroy()
      self.destroy()