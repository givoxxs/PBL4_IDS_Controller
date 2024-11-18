# views/panel_threats.py
import tkinter as tk
from tkinter import ttk

class PanelThreats(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
        self.display_threats() # Hiển thị threats ban đầu
        self.page = 1 # Khởi tạo page
        self.per_page = 100 # mỗi trang 100 dòng

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


    def display_threats(self, page = 1):
        # """Hiển thị danh sách các mối đe dọa."""
        # threats = self.controller.get_threats()
        # # Xóa dữ liệu cũ trên Treeview
        # for i in self.tree.get_children():
        #     self.tree.delete(i)

        # # Hiển thị threats
        # for threat in threats:
        #     self.tree.insert("", tk.END, values = (threat["src_IP"], threat["dst_IP"], threat["protocol"], threat["occur"], threat['last_seen']))

        """Hiển thị danh sách các mối đe dọa (tối ưu)."""
        threats = self.controller.get_threats()
        current_threats = {}  # Lưu trữ threat hiện có trên Treeview
        
        self.page = page # set page hiện tại
        self.update_pagination() # tính toán số trang

        # Lấy danh sách các item hiện có trên Treeview
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            key = (values[0], values[1], values[2])  # Tạo key từ src_IP, dst_IP, protocol
            current_threats[key] = item

        # Cập nhật Treeview
        for threat in threats:
            key = (threat["src_IP"], threat["dst_IP"], threat["protocol"])
            if key in current_threats:
                # Cập nhật threat hiện có
                item = current_threats[key]
                self.tree.item(item, values=(threat["src_IP"], threat["dst_IP"], threat["protocol"], threat["occur"], threat['last_seen']))
                del current_threats[key]  # Xóa khỏi current_threats
            else:
                # Thêm threat mới
                self.tree.insert("", tk.END, values=(threat["src_IP"], threat["dst_IP"], threat["protocol"], threat["occur"], threat['last_seen']))

        # Xóa các threat không còn tồn tại
        for item in current_threats.values():
            self.tree.delete(item)

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
            
    def update_pagination(self):
        """Cập nhật thông tin phân trang."""

        total_threats = self.controller.get_total_threats()  # Lấy tổng số threats
        total_pages = (total_threats + self.per_page - 1) // self.per_page  # Tính tổng số trang
        self.page_label.config(text=f"Page {self.page}/{total_pages}")

        # Enable/disable prev/next buttons
        self.prev_button.config(state=tk.NORMAL if self.page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.page < total_pages else tk.DISABLED)
        
    # Thêm các hàm prev_page, next_page tương tự như PanelLogs
    def prev_page(self):
        """Chuyển đến trang trước."""
        if self.page > 1:
            self.page -= 1
            self.display_threats(self.page) # Refresh data
            self.update_pagination() # Update buttons
    
    def next_page(self):
        """Chuyển đến trang sau."""
        total_threats = self.controller.get_total_threats()
        total_pages = (total_threats + self.per_page - 1) // self.per_page
        if self.page < total_pages:
            self.page += 1
            self.display_threats(self.page)
            self.update_pagination()
        