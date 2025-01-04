import tkinter as tk
from tkinter import ttk
from models.alert import Alert
from tkinter import messagebox
from controllers.ids_controller import IDSController

class PanelLogs(tk.Frame):
    def __init__(self, parent, controller: IDSController):
        super().__init__(parent)
        self.controller = controller
        self.page = 1  # Khởi tạo page
        self.per_page = 100  # mỗi trang 100 dòng
        self.current_protocol_filter = "Tất cả" # Khởi tạo bộ lọc giao thức mặc định
        self.current_priority_filter = "Tất cả" # Khởi tạo bộ lọc priority mặc định
        self.create_widgets()
        self.display_alerts()  # Hiển thị alert ban đầu

    def create_widgets(self):
        """Tạo các widget cho Panel Logs."""

        # Frame chứa các widget lọc
        filter_frame = tk.Frame(self)
        filter_frame.pack(fill="x")

        # Label và OptionMenu lọc theo giao thức
        protocol_label = tk.Label(filter_frame, text="Lọc theo giao thức:")
        protocol_label.pack(side="left")
        
        protocols = ["Tất cả"] + self.controller.get_all_protocols()
        self.protocol_var = tk.StringVar(self)
        self.protocol_var.set("Tất cả")  # Giá trị mặc định
        protocol_dropdown = ttk.OptionMenu(filter_frame, self.protocol_var, *protocols, command=self.apply_filters)
        protocol_dropdown.pack(side="left", padx=5)
        
         # Label và OptionMenu lọc theo độ ưu tiên
        priority_label = tk.Label(filter_frame, text="Lọc theo độ ưu tiên:")
        priority_label.pack(side="left", padx = (20,0))

        priorities = ["Tất cả"] + list(set([alert.priority for alert in self.controller.get_alerts(filter_criteria=None, page=1, per_page= self.per_page)]))
        self.priority_var = tk.StringVar(self)
        self.priority_var.set("Tất cả") # Giá trị mặc định
        priority_dropdown = ttk.OptionMenu(filter_frame, self.priority_var, *priorities, command=self.apply_filters)
        priority_dropdown.pack(side="left", padx = 5)
        
        # Tạo Treeview widget
        columns = Alert.get_columns()  # Gọi phương thức get_columns()
        self.tree = ttk.Treeview(self, columns=tuple(columns), show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)  # hoặc width theo ý bạn
        self.tree.pack(fill="both", expand=True)

        # Thêm nút phân trang
        pagination_frame = tk.Frame(self)
        pagination_frame.pack(fill="x")

        self.prev_button = ttk.Button(pagination_frame, text="Previous", command=self.prev_page, state=tk.DISABLED)  # vô hiệu hóa ban đầu
        self.prev_button.pack(side=tk.LEFT)

        self.page_label = tk.Label(pagination_frame, text="Page 1/1")
        self.page_label.pack(side=tk.LEFT)

        self.next_button = ttk.Button(pagination_frame, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.LEFT)
    
    def apply_filters(self, event=None):
         """Áp dụng bộ lọc và hiển thị alert mới."""
         self.current_protocol_filter = self.protocol_var.get()
         self.current_priority_filter = self.priority_var.get()
         self.page = 1 # Reset page to 1 when applying filters
         self.display_alerts() # Hiển thị alert với bộ lọc mới


    def display_alerts(self):
        """Hiển thị alerts với bộ lọc giao thức và priority."""
        # Xóa dữ liệu cũ trong tree
        for i in self.tree.get_children():
            self.tree.delete(i)
        
        # Tạo filter_criteria dictionary
        filter_criteria = {}
        if self.current_protocol_filter.lower() != "tất cả":
             filter_criteria["protocol"] = self.current_protocol_filter
        if self.current_priority_filter.lower() != "tất cả":
             filter_criteria["priority"] = self.current_priority_filter

        if not filter_criteria:
             filter_criteria = None

        self.update_pagination(filter_criteria)  # tính toán số trang và cập nhật lại page label

        # Lấy dữ liệu theo trang hiện tại
        alerts = self.controller.get_alerts(filter_criteria=filter_criteria, page=self.page, per_page=self.per_page)
        
        for alert in alerts:
           self.tree.insert("", tk.END, values=alert.to_tuple())

    def update_pagination(self, filter_criteria=None):
        """Cập nhật thông tin phân trang."""
        total_alerts = self.controller.get_total_alerts(filter_criteria=filter_criteria)  # tính tổng alert với filter hiện tại
        total_pages = (total_alerts + self.per_page - 1) // self.per_page  # Tính tổng số trang
        self.page_label.config(text=f"Page {self.page}/{total_pages}")
        
        # kích hoạt/vô hiệu hóa button prev và next
        self.prev_button.config(state=tk.NORMAL if self.page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.page < total_pages else tk.DISABLED)


    def prev_page(self):
         """Chuyển đến trang trước."""
         if self.page > 1:
            self.page -= 1
            self.display_alerts()  # Refresh data


    def next_page(self):
         """Chuyển đến trang sau."""
         # Xây dựng filter_criteria
         filter_criteria = {}
         if self.current_protocol_filter.lower() != "tất cả":
             filter_criteria["protocol"] = self.current_protocol_filter
         if self.current_priority_filter.lower() != "tất cả":
             filter_criteria["priority"] = self.current_priority_filter
            
         if not filter_criteria:
            filter_criteria = None
            
         total_alerts = self.controller.get_total_alerts(filter_criteria=filter_criteria) # Tính tổng số alerts với filter_criteria
         total_pages = (total_alerts + self.per_page - 1) // self.per_page
         if self.page < total_pages:
            self.page += 1
            self.display_alerts() # call with current filter

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