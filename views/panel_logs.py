import tkinter as tk
from tkinter import ttk
from models.alert import Alert
from tkinter import messagebox

class PanelLogs(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.create_widgets()
        self.display_alerts() # Hiển thị alert ban đầu
        self.page = 1 # Khởi tạo page
        self.per_page = 100 # mỗi trang 100 dòng


    def create_widgets(self):
        """Tạo các widget cho Panel Logs."""

        # Tạo Treeview widget
        columns = Alert.get_columns() # Gọi phương thức get_columns()
        self.tree = ttk.Treeview(self, columns=tuple(columns), show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100) # hoặc width theo ý bạn
        self.tree.pack(fill="both", expand=True)

         # Thêm nút phân trang
        pagination_frame = tk.Frame(self)
        pagination_frame.pack(fill="x")

        self.prev_button = ttk.Button(pagination_frame, text="Previous", command=self.prev_page, state = tk.DISABLED) # vô hiệu hóa ban đầu
        self.prev_button.pack(side = tk.LEFT)

        self.page_label = tk.Label(pagination_frame, text="Page 1/1")
        self.page_label.pack(side=tk.LEFT)

        self.next_button = ttk.Button(pagination_frame, text="Next", command=self.next_page)
        self.next_button.pack(side = tk.LEFT)


    # def display_alerts(self, protocol_filter = "Tất cả"):
    #     """Hiển thị alerts trong Treeview."""
    #     alerts = self.controller.get_alerts()  # Lấy dữ liệu từ controller
    #     alerts = alerts[-100:]  # Chỉ lấy 100 dòng cuối cùng
    #     for i in self.tree.get_children(): # Xóa dữ liệu cũ (nếu có)
    #         self.tree.delete(i)

    #     for alert in alerts:
    #         self.tree.insert("", tk.END, values=alert.to_tuple())
            
    def display_alerts(self, protocol_filter = "Tất cả"): # thêm tham số lọc
        # ... (xóa dữ liệu cũ trong tree)
        for i in self.tree.get_children():
            self.tree.delete(i)
            

        self.current_protocol_filter = protocol_filter # Biến lưu trữ filter hiện tại

        self.update_pagination() # tính toán số trang và cập nhật lại page label

        # Lấy dữ liệu theo trang hiện tại
        alerts = self.controller.get_alerts(protocol=protocol_filter, page=self.page, per_page = self.per_page)

        for alert in alerts:
            self.tree.insert("", tk.END, values=alert.to_tuple())
            
    def update_pagination(self):
        """Cập nhật thông tin phân trang."""
        total_alerts = self.controller.get_total_alerts(protocol = self.current_protocol_filter) # tính tổng alert với filter hiện tại
        total_pages = (total_alerts + self.per_page -1) // self.per_page # Tính tổng số trang
        self.page_label.config(text=f"Page {self.page}/{total_pages}")
        # kích hoạt/vô hiệu hóa button prev và next
        self.prev_button.config(state=tk.NORMAL if self.page> 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.page < total_pages else tk.DISABLED)

        
        if self.page == 1:
            self.prev_button.config(state=tk.DISABLED)
        else:
            self.prev_button.config(state=tk.NORMAL)
            
        if total_pages > self.page :
            self.next_button.config(state=tk.NORMAL)
        else:
            self.next_button.config(state=tk.DISABLED)
            
    def prev_page(self):
        """Chuyển đến trang trước."""

        if self.page > 1:
            self.page -= 1
            self.display_alerts(self.current_protocol_filter) # Refresh data
            self.update_pagination() # Update buttons


    def next_page(self):
        """Chuyển đến trang sau."""
        
        total_alerts = self.controller.get_total_alerts(protocol = self.current_protocol_filter) # Tính lại số lượng alert sau khi filter
        total_pages = (total_alerts + self.per_page -1) // self.per_page
        if self.page < total_pages:
            self.page += 1
            self.display_alerts(self.current_protocol_filter)
            self.update_pagination() # Update pagination buttons

    def search_alerts(self):
        search_term = self.search_term.get()

        if not search_term:
            messagebox.showwarning("Lỗi", "Vui lòng nhập từ khóa tìm kiếm.")
            return

        # Thêm phân trang cho tìm kiếm
        self.current_search_term = search_term
        self.page = 1
        self.update_search_pagination()
        filtered_alerts = self.controller.search_alerts(search_term, page=self.page, per_page=self.per_page)

        if filtered_alerts:
            for i in self.tree.get_children():
                self.tree.delete(i)
            for alert in filtered_alerts:
                self.tree.insert("", tk.END, values=alert.to_tuple())
        else:
            # Hiển thị thông báo nếu không có kết quả
            self.tree.insert("", tk.END, values=("Không tìm thấy kết quả nào", "", "", "", "", "", "", "", "", "", "", "", "", ""))
    
    def update_search_pagination(self):
        """Cập nhật thông tin phân trang khi tìm kiếm."""
        total_alerts = self.controller.get_total_search_result(self.current_search_term)
        total_pages = (total_alerts + self.per_page - 1) // self.per_page
        self.page_label.config(text=f"Page {self.page}/{total_pages}")

        # Enable/disable prev/next buttons
        self.prev_button.config(state=tk.NORMAL if self.page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.page < total_pages else tk.DISABLED)