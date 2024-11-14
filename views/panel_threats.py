# views/panel_threats.py
import tkinter as tk
from tkinter import ttk

class PanelThreats(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
        self.display_threats() # Hiển thị threats ban đầu

    def create_widgets(self):
        """Tạo các widget cho Panel Threats."""

        # Tạo Treeview
        columns = ("Source IP", "Destination IP", "Protocol", "Occurrences", "Last Seen") # Thêm cột Last Seen
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

        # Frame chứa các nút bấm
        button_frame = tk.Frame(self)
        button_frame.pack()


        actions = ["safe", "ignore", "limit", "block"]
        for action in actions:
            button = ttk.Button(button_frame, text=action.capitalize(), command = lambda action=action: self.handle_threat_action(action) )
            button.pack(side=tk.LEFT, padx=5, pady = 5)


    def display_threats(self):
        """Hiển thị danh sách các mối đe dọa."""
        threats = self.controller.get_threats()
        # Xóa dữ liệu cũ trên Treeview
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Hiển thị threats
        for threat in threats:
            self.tree.insert("", tk.END, values = (threat["src_IP"], threat["dst_IP"], threat["protocol"], threat["occur"], threat['last_seen']))


    def handle_threat_action(self, action):
        """Xử lý hành động của người dùng trên threat."""

        selected_item = self.tree.selection() # lấy threat được chọn
        if selected_item:
            threat_data = self.tree.item(selected_item[0])["values"]  # Lấy dữ liệu threat
            # Chuyển đổi threat_data thành dictionary để dễ xử lý
            threat_dict = {
                "src_IP": threat_data[0],
                "dst_IP": threat_data[1],
                "protocol": threat_data[2],
                "occur": threat_data[3],
                "last_seen": threat_data[4]
            }
            result = self.controller.handle_threat_action(threat_dict, action)  # Gọi controller để xử lý
            print(result) # or show messagebox
            self.display_threats() # update treeview