import tkinter as tk
from tkinter import ttk
from utils.plotter import Plotter
from utils import check_services_status

class PanelDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.update_data_id = None
        self.check_snort_status_id = None
        self.controller = controller
        self.create_widgets()
        self.update_data()
        
    def create_widgets(self):
        summary_frame = ttk.LabelFrame(self, text="Summary")
        summary_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") # nsew: đàn hồi theo tất cả các hướng
        
        self.total_alerts_label = ttk.Label(summary_frame, text="Total alerts: 0")  # Tổng số alert
        self.total_alerts_label.pack(pady=5)
        
        self.unhandled_alerts_label = ttk.Label(summary_frame, text="Unhandled alerts: 0")  # Chưa xử lý
        self.unhandled_alerts_label.pack(pady=5)

        #Frame biểu đồ
        chart_frame = ttk.LabelFrame(self, text="Charts")
        chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        plot_time_button = ttk.Button(chart_frame, text="Plot alerts over time", command=self.plot_alerts_time)
        plot_time_button.pack(pady=5)
                
        plot_ips_button = ttk.Button(chart_frame, text="Plot Top Attacking IPs", command=self.plot_top_ips)
        plot_ips_button.pack(pady=5)
        
        plot_types_button = ttk.Button(chart_frame, text="Plot Alert Types", command=self.plot_alert_types)
        plot_types_button.pack(pady=5)
        
        plot_rules_button = ttk.Button(chart_frame, text="Plot Top Alert Rules", command=self.plot_top_rules)
        plot_rules_button.pack(pady=5)
        
        # Frame trạng thái Snort
        status_frame = ttk.LabelFrame(self, text="Snort Status")
        status_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")
        
        self.snort_status_label = ttk.Label(status_frame, text="Snort status: Checking...")
        self.snort_status_label.pack(pady=5)
            
        self.check_snort_status()
        
        # Frame Top IP
        top_ips_frame = ttk.LabelFrame(self, text="Top Attacking IPs")
        top_ips_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        
        # Frame Top Rules
        top_rules_frame = ttk.LabelFrame(self, text="Top Alert Rules")
        top_rules_frame.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        
        self.columnconfigure(0, weight=2) # Cột biểu đồ rộng hơn
        self.columnconfigure(1, weight=1) # Cột trạng thái Snort nhỏ hơn
        self.columnconfigure(2, weight=1) # Cột top IPs/rules nhỏ hơn
        self.rowconfigure(0, weight=1)    # Hàng trên cùng và hàng dưới cùng có cùng chiều cao
        self.rowconfigure(1, weight=1)
        
    def update_data(self):
        """Cập nhật dữ liệu trên dashboard."""
        alerts = self.controller.get_alerts()
        self.total_alerts_label.config(text=f"Total Alerts: {len(alerts)}")

        unhandled_alerts = [alert for alert in alerts if not alert.action_taken]
        self.unhandled_alerts_label.config(text=f"Unhandled Alerts: {len(unhandled_alerts)}")
        
        if self.update_data_id:  # Kiểm tra xem có id after nào đang chạy không
            self.after_cancel(self.update_data_id)

        self.update_data_id = self.after(300000, self.update_data) # 5 phút
        # self.after(100000, self.update_data) # Cập nhật sau mỗi 100 giây
        
    def plot_alerts_time(self):
        alerts = self.controller.get_alerts()
        Plotter.plot_alerts_over_time(alerts)

    def plot_top_ips(self):
        alerts = self.controller.get_alerts()
        Plotter.plot_top_attack_ips(alerts)

    def plot_alert_types(self):
        alerts = self.controller.get_alerts()
        Plotter.plot_alert_types(alerts)

    def plot_top_rules(self):
        alerts = self.controller.get_alerts()
        Plotter.plot_top_rules(alerts)

    def check_snort_status(self):
        """Kiểm tra trạng thái Snort và cập nhật lên giao diện."""
        # ufw_status, snort_status = check_services_status()
        ufw_status = "Status: active"
        snort_status = "Status: active"
        
        status_text = f"UFW Status:\n{ufw_status}\n\nSnort Status:\n{snort_status}"
        self.snort_status_label.config(text=status_text)
        self.after(300000, self.check_snort_status) # Kiểm tra lại sau 100 iây