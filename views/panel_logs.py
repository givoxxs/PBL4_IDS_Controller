import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from models.alert import Alert
from controllers.ids_controller import IDSController

class PanelLogs(tk.Frame):
    def __init__(self, parent, controller: IDSController):
        super().__init__(parent)
        self.controller = controller
        self.page = 1  # Current page
        self.per_page = 100  # Number of alerts per page
        self.current_protocol_filter = "Tất cả"  # Default filter
        self.filter_criteria = None  # Filter criteria dictionary
        self.create_widgets()
        self.display_alerts()  # Display initial alerts

    def create_widgets(self):
        """Create the widgets for the Panel Logs."""
        # Filter frame
        filter_frame = tk.Frame(self)
        filter_frame.pack(fill="x")

        # Protocol filter label and dropdown
        protocol_label = tk.Label(filter_frame, text="Lọc theo giao thức:")
        protocol_label.pack(side="left")

        self.protocol_var = tk.StringVar(self)
        protocols = ["Tất cả"] + self.controller.get_all_protocols()
        self.protocol_var.set("Tất cả")

        self.protocol_dropdown = ttk.OptionMenu(
            filter_frame, 
            self.protocol_var, 
            "Tất cả", 
            *protocols, 
            command=self.apply_filters
        )
        self.protocol_dropdown.pack(side="left", padx=5)

        # Treeview to display alerts
        columns = Alert.get_columns()
        self.tree = ttk.Treeview(self, columns=tuple(columns), show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

        # Pagination controls
        pagination_frame = tk.Frame(self)
        pagination_frame.pack(fill="x")

        self.prev_button = ttk.Button(pagination_frame, text="Previous", command=self.prev_page, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT)

        self.page_label = tk.Label(pagination_frame, text="Page 1/1")
        self.page_label.pack(side=tk.LEFT)

        self.next_button = ttk.Button(pagination_frame, text="Next", command=self.next_page)
        self.next_button.pack(side=tk.LEFT)

    def apply_filters(self, event=None):
        """Apply the selected filter and refresh the alerts display."""
        selected_protocol = self.protocol_var.get()

        # Update filter criteria based on selected protocol
        if selected_protocol != "Tất cả":
            self.filter_criteria = {"protocol": selected_protocol}
        else:
            self.filter_criteria = None

        # Reset to the first page and refresh the display
        self.page = 1
        self.display_alerts()

    def display_alerts(self):
        """Display alerts based on the current filter and pagination."""
        # Clear existing treeview data
        for i in self.tree.get_children():
            self.tree.delete(i)

        # Fetch alerts based on filter and pagination
        alerts = self.controller.get_alerts(filter_criteria=self.filter_criteria, page=self.page, per_page=self.per_page)
        for alert in alerts:
            self.tree.insert("", tk.END, values=alert.to_tuple())

        # Update pagination controls
        self.update_pagination()

    def update_pagination(self):
        """Update pagination controls and labels."""
        total_alerts = self.controller.get_total_alerts(filter_criteria=self.filter_criteria)
        total_pages = (total_alerts + self.per_page - 1) // self.per_page

        # Update page label
        self.page_label.config(text=f"Page {self.page}/{total_pages}")

        # Enable/disable pagination buttons
        self.prev_button.config(state=tk.NORMAL if self.page > 1 else tk.DISABLED)
        self.next_button.config(state=tk.NORMAL if self.page < total_pages else tk.DISABLED)

    def prev_page(self):
        """Navigate to the previous page."""
        if self.page > 1:
            self.page -= 1
            self.display_alerts()

    def next_page(self):
        """Navigate to the next page."""
        total_alerts = self.controller.get_total_alerts(filter_criteria=self.filter_criteria)
        total_pages = (total_alerts + self.per_page - 1) // self.per_page
        if self.page < total_pages:
            self.page += 1
            self.display_alerts()
