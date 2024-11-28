import tkinter as tk
from tkinter import ttk
from models.alert import Alert
from tkinter import messagebox

class PanelLogs(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.page = 1 # Khởi tạo page
        self.per_page = 100 # mỗi trang 100 dòng
        self.create_widgets()
        self.display_alerts() # Hiển thị alert ban đầu


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
            
    def display_alerts(self, protocol_filter = "Tất cả"): # thêm tham số lọc
        # ... (xóa dữ liệu cũ trong tree)
        for i in self.tree.get_children():
            self.tree.delete(i)
            

        self.current_protocol_filter = protocol_filter # Biến lưu trữ filter hiện tại
        
        # Tạo filter_criteria dictionary
        if protocol_filter.lower() == "tất cả":
            filter_criteria = None  # Không lọc nếu là "Tất cả"
        else:
            filter_criteria = {"protocol": protocol_filter}

        self.update_pagination(filter_criteria) # tính toán số trang và cập nhật lại page label

        # Lấy dữ liệu theo trang hiện tại
        alerts = self.controller.get_alerts(filter_criteria=filter_criteria, page=self.page, per_page=self.per_page)

        for alert in alerts:
            self.tree.insert("", tk.END, values=alert.to_tuple())
            
    def update_pagination(self, filter_criteria=None):
        """Cập nhật thông tin phân trang."""
        total_alerts = self.controller.get_total_alerts(filter_criteria=filter_criteria)  # tính tổng alert với filter hiện tại
        total_pages = (total_alerts + self.per_page - 1) // self.per_page  # Tính tổng số trang
        self.page_label.config(text=f"Page {self.page}/{total_pages}")
        
        total_alerts = self.controller.get_total_alerts(filter_criteria=filter_criteria) # tính tổng alert với filter hiện tại
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
            
            if hasattr(self, 'current_protocol_filter'):
                filter = self.current_protocol_filter
            else:
                filter = "Tất cả"
            if filter.lower() == "tất cả":
                filter_criteria = None  # Không lọc nếu là "Tất cả"
            else:
                filter_criteria = {"protocol": filter}
            self.display_alerts(filter) # Refresh data
            self.update_pagination(filter_criteria) # Update buttons with filter


    def next_page(self):
        """Chuyển đến trang sau."""
        if hasattr(self, 'current_protocol_filter'):
            filter = self.current_protocol_filter
        else:
            filter = "Tất cả"


        if filter.lower() == "tất cả":
            filter_criteria = None  # Không lọc nếu là "Tất cả"
        else:
            filter_criteria = {"protocol": filter}

        total_alerts = self.controller.get_total_alerts(filter_criteria=filter_criteria) # Tính tổng số alerts với filter_criteria
        total_pages = (total_alerts + self.per_page - 1) // self.per_page
        if self.page < total_pages:
            self.page += 1
            self.display_alerts(filter) # call with current filter
            self.update_pagination(filter_criteria) # update pagination info

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
    
    def update_search_pagination(self, filter_criteria=None):
        """Cập nhật thông tin phân trang khi tìm kiếm."""
        
        total_alerts = self.controller.get_total_alerts(filter_criteria=filter_criteria)  # Truyền filter_criteria
        total_pages = (total_alerts + self.per_page - 1) // self.per_page
        self.page_label.config(text=f"Page {self.page}/{total_pages}")

        # Enable/disable prev/next buttons
        self.prev_button.config(state=tk.NORMAL if self.page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.page < total_pages else tk.DISABLED)