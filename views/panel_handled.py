import tkinter as tk
from tkinter import ttk
from models.alert import Alert
from tkinter import messagebox
from controllers.ids_controller import IDSController

class PanelHandled(tk.Frame):
    def __init__(self, parent, controller: IDSController):
        super().__init__(parent)
        self.controller = controller
        self.page = 1 # Khởi tạo page
        self.per_page = 100 # mỗi trang 100 dòng
        self.create_widgets()
        self.display_alerts() 

    def create_widgets(self):
        """Tạo các widget cho Panel Handled."""

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
            
    def display_alerts(self, filter_criteria={'action_taken': 1}):
        print("Loading handled panel")
        for i in self.tree.get_children():
            self.tree.delete(i)

        self.filter_criteria = filter_criteria
        self.update_pagination(filter_criteria)

        alerts = self.controller.get_alerts_by_action_taken(
            filter_criteria=filter_criteria, page=self.page, per_page=self.per_page
        )

        if not alerts:
            self.tree.insert("", tk.END, values=("No data",) * len(Alert.get_columns()))
            return

        for alert_dict in alerts:
            try:
                alert_dict = alert_dict.to_dict()
                alert = Alert(
                    timestamp=alert_dict.get("timestamp", "Unknown"),
                    src_IP=alert_dict.get("src_IP", "Unknown"),
                    dst_IP=alert_dict.get("dst_IP", "Unknown"),
                    protocol=alert_dict.get("protocol", "Unknown"),
                    action=alert_dict.get("action", "Unknown"),
                    gid=alert_dict.get("gid", "Unknown"),
                    sid=alert_dict.get("sid", "Unknown"),
                    rev=alert_dict.get("rev", "Unknown"),
                    msg=alert_dict.get("msg", "Unknown"),
                    service=alert_dict.get("service", "Unknown"),
                    src_Port=alert_dict.get("src_Port", 0),
                    dst_Port=alert_dict.get("dst_Port", 0),
                    action_taken=alert_dict.get("action_taken", "Unknown"),
                    priority=alert_dict.get("priority", "Unknown"),
                    occur=alert_dict.get("occur", 0),
                    last_seen= alert_dict.get("last-seen", "Unkown")
                )
                self.tree.insert("", tk.END, values=alert.to_tuple())
            except Exception as e:
                print(f"Error displaying alert: {e}")
                continue


            
    def update_pagination(self, filter_criteria=None):
        """Cập nhật thông tin phân trang."""
        total_alerts = self.controller.get_total_alerts(filter_criteria=filter_criteria)  # tính tổng alert với filter hiện tại
        total_pages = (total_alerts + self.per_page - 1) // self.per_page  # Tính tổng số trang
        self.page_label.config(text=f"Page {self.page}/{total_pages}")  # Hiển thị thông tin phân trang
        
        # Kích hoạt/vô hiệu hóa button prev và next
        self.prev_button.config(state=tk.NORMAL if self.page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.page < total_pages else tk.DISABLED)


    def prev_page(self):
        """Chuyển đến trang trước."""
        if self.page > 1:
            self.page -= 1
            self.display_threats(self.page)

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