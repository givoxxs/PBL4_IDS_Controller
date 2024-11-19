import tkinter as tk
from tkinter import ttk
from utils.plotter import Plotter
from utils.check_services_status import check_service_status
import matplotlib.pyplot as plt # type: ignore
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class PanelDashboard(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.alerts = []
        self.create_widgets()
        self.update_data()
        
    def create_widgets(self):
        # Frame tổng quán
        summary_frame = ttk.LabelFrame(self, text="Summary")
        summary_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew") # nsew: đàn hồi theo tất cả các hướng
        
        self.total_alerts_label = ttk.Label(summary_frame, text="Total alerts: 0")  # Tổng số alert
        self.total_alerts_label.pack(pady=5)
        
        self.unhandled_alerts_label = ttk.Label(summary_frame, text="Unhandled alerts: 0")  # Chưa xử lý
        self.unhandled_alerts_label.pack(pady=5)

        #Frame biểu đồ
        chart_frame = ttk.LabelFrame(self, text="Charts")
        chart_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        
        self.fig_time, self.ax_time = plt.subplots()
        self.canvas_time = FigureCanvasTkAgg(self.fig_time, master=chart_frame)
        self.canvas_time.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        self.fig_ips, self.ax_ips = plt.subplots()
        self.canvas_ips = FigureCanvasTkAgg(self.fig_ips, master=chart_frame)
        self.canvas_ips.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas_ips.get_tk_widget().pack_forget() #  ẩn đi ban đầu
        
        self.fig_types, self.ax_types = plt.subplots()
        self.canvas_types = FigureCanvasTkAgg(self.fig_types, master=chart_frame)
        self.canvas_types.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas_types.get_tk_widget().pack_forget()

        self.fig_rules, self.ax_rules = plt.subplots()
        self.canvas_rules = FigureCanvasTkAgg(self.fig_rules, master=chart_frame)
        self.canvas_rules.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas_rules.get_tk_widget().pack_forget()
        
        chart_buttons_frame = tk.Frame(chart_frame)
        chart_buttons_frame.pack()
        
        self.chart_buttons = {}
        chart_types = ["time", "ips", "types", "rules"]
        for chart_type in chart_types:
            button = tk.Button(chart_buttons_frame, text=f"Plot {chart_type}", command=lambda chart_type=chart_type: self.switch_chart(chart_type))
            button.pack(side = tk.LEFT, padx=5)
            self.chart_buttons[chart_type] = button
        
        # Frame trạng thái Snorts
        status_frame = ttk.LabelFrame(self, text="Snort Status")
        status_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=10, sticky="nsew")

        self.snort_status_label = ttk.Label(status_frame, text="Snort status: Checking...")
        self.snort_status_label.pack(pady=5)

        self.check_snort_status()
        
        # Frame Top IP
        top_ips_frame = ttk.LabelFrame(self, text="Top Attacking IPs")
        top_ips_frame.grid(row=0, column=2, padx=10, pady=(10, 0), sticky="nsew")
        
        self.top_ips_listbox = tk.Listbox(top_ips_frame)
        self.top_ips_listbox.pack(fill=tk.BOTH, expand=True) # listbox sẽ expand
        
        
        # Frame Top Rules
        top_rules_frame = ttk.LabelFrame(self, text="Top Alert Rules")
        top_rules_frame.grid(row=1, column=2, padx=10, pady=(10,0), sticky="nsew")
        
        self.top_rules_listbox = tk.Listbox(top_rules_frame)
        self.top_rules_listbox.pack(fill=tk.BOTH, expand=True)
        
        self.columnconfigure(0, weight=2) # Cột biểu đồ rộng hơn
        self.columnconfigure(1, weight=1) # Cột trạng thái Snort nhỏ hơn
        self.columnconfigure(2, weight=1) # Cột top IPs/rules nhỏ hơn
        self.rowconfigure(0, weight=1)    # Hàng trên cùng và hàng dưới cùng có cùng chiều cao
        self.rowconfigure(1, weight=1)
        
        # Nút Refresh
        refresh_button = ttk.Button(self, text="Refresh", command=self.update_data)
        refresh_button.grid(row=2, column=0, columnspan=3, pady=(10,0))  # Thay đổi vị trí nút refresh
        
    def update_data(self):
        """Cập nhật dữ liệu trên dashboard."""
        print ("Updating data...")
        self.alerts = self.controller.get_alerts()
        self.total_alerts_label.config(text=f"Total Alerts: {len(self.alerts)}")
        unhandled_alerts = [alert for alert in self.alerts if not alert.action_taken]
        self.unhandled_alerts_label.config(text=f"Unhandled Alerts: {len(unhandled_alerts)}")
        
        # Cập nhật tất cả các biểu đồ khi dữ liệu thay đổi
        self.plot_alerts_time()
        self.plot_top_ips()
        self.plot_alert_types()
        self.plot_top_rules()


        self.update_top_ips_listbox()
        self.update_top_rules_listbox()
        print("Data updated successfully")
        self.after(300000, self.update_data) # Cập nhật sau mỗi 5 phút
                
    def switch_chart(self, chart_type):
        for type, canvas in [("time", self.canvas_time), ("ips", self.canvas_ips), ("types", self.canvas_types), ("rules", self.canvas_rules)]:
            if type == chart_type:
                canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)  # Show chart
                self.chart_buttons[type].config(relief=tk.SUNKEN)  # Depress button
            else:
                canvas.get_tk_widget().pack_forget()  # Hide chart
                self.chart_buttons[type].config(relief=tk.RAISED)  # Raise button
        
    def plot_alerts_time(self):
        
        """Vẽ biểu đồ số lượng alerts theo thời gian."""

        Plotter.plot_alerts_over_time(self.ax_time, self.alerts)
        self.canvas_time.draw()

    def plot_top_ips(self):
        # def plot_top_ips(self):
        """Vẽ biểu đồ top IP tấn công."""

        Plotter.plot_top_attack_ips(self.ax_ips, self.alerts)
        self.canvas_ips.draw()

    def plot_alert_types(self):
        """Vẽ biểu đồ loại tấn công."""

        Plotter.plot_alert_types(self.ax_types, self.alerts)
        self.canvas_types.draw()

    def plot_top_rules(self):
        """Vẽ biểu đồ top rules."""
        Plotter.plot_top_rules(self.ax_rules, self.alerts)
        self.canvas_rules.draw()

    def check_snort_status(self):
        """Kiểm tra trạng thái Snort và cập nhật lên giao diện."""
        ufw_status, snort_status = check_services_status()
        # ufw_status = "Status: active"
        # snort_status = "Status: active"
        
        status_text = f"UFW Status:\n{ufw_status}\n\nSnort Status:\n{snort_status}"
        self.snort_status_label.config(text=status_text)
        self.after(100000, self.check_snort_status) 
        
    def update_top_ips_listbox(self):
        """Cập nhật Top Attacking IPs Listbox."""
        top_ips = Plotter.get_top_attack_ips(self.alerts)
        self.top_ips_listbox.delete(0, tk.END)  # Xóa dữ liệu cũ
        for ip, count in top_ips.items():
            self.top_ips_listbox.insert(tk.END, f"{ip}: {count}")


    def update_top_rules_listbox(self):
        """Cập nhật Top Alert Rules Listbox."""
        top_rules = Plotter.get_top_rules_2(self.alerts)
        self.top_rules_listbox.delete(0, tk.END)
        for rule, count in top_rules.items():
            self.top_rules_listbox.insert(tk.END, f"{rule}: {count}")