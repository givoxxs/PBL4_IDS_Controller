# In views/panel_threats.py
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from controllers.ids_controller import IDSController
import logging

logger = logging.getLogger(__name__)


class PanelThreats(tk.Frame):
    def __init__(self, parent, controller: IDSController):
        super().__init__(parent)
        self.controller = controller
        self.page = 1
        self.per_page = 10
        self.default_max_priority = 3 # set the default value here
        self.create_widgets()
        self.display_threats()

    def create_widgets(self):
        """Tạo các widget cho Panel Threats."""
        columns = (
            "Source IP",
            "Destination IP",
            "Protocol",
            "Action Taken",
            "Priority",
            "Occurrences",
            "Last Seen",
        )
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        self.tree.pack(fill="both", expand=True)

        button_frame = tk.Frame(self)
        button_frame.pack()

        self.prev_button = ttk.Button(
            button_frame, text="Previous", command=self.prev_page, state=tk.DISABLED
        )
        self.prev_button.pack(side=tk.LEFT)

        self.page_label = tk.Label(button_frame, text="Page 1/1")
        self.page_label.pack(side=tk.LEFT)

        self.next_button = ttk.Button(
            button_frame, text="Next", command=self.next_page
        )
        self.next_button.pack(side=tk.LEFT)

        actions = ["safe", "ignore", "limit", "block"]
        for action in actions:
            button = ttk.Button(
                button_frame,
                text=action.capitalize(),
                command=lambda action=action: self.handle_threat_action(action),
            )
            button.pack(side=tk.LEFT, padx=5, pady=5)
    
    def display_threats(self, page=1):
        """Hiển thị danh sách các mối đe dọa."""
        logger.info("Loading panel threats")
        for item in self.tree.get_children():
            self.tree.delete(item)

        offset = (page - 1) * self.per_page
        threats = self.controller.get_threats(limit=self.per_page, offset=offset, priority = self.default_max_priority) # use the default priority
        current_threats = {}
        self.page = page
        self.update_pagination()

        for item in self.tree.get_children():
           values = self.tree.item(item)["values"]
           key = (
               values[0],
               values[1],
               values[2],
           )
           current_threats[key] = item


        for threat in threats:
          key = (threat["src_IP"], threat["dst_IP"], threat["protocol"])
          if key in current_threats:
               item = current_threats[key]
               self.tree.item(
                    item,
                    values=(
                        threat["src_IP"],
                        threat["dst_IP"],
                        threat["protocol"],
                        threat.get("action_taken", 0),
                        threat.get("priority", "N/A"),
                        threat["occur"],
                        threat["last_seen"],
                    ),
                )
               del current_threats[key]
          else:
               self.tree.insert(
                    "",
                    tk.END,
                    values=(
                        threat["src_IP"],
                        threat["dst_IP"],
                        threat["protocol"],
                        threat.get("action_taken", 0),
                        threat.get("priority", "N/A"),
                        threat["occur"],
                        threat["last_seen"],
                    ),
                )

        for item in current_threats.values():
              self.tree.delete(item)
    def handle_threat_action(self, action: str):
         """Xử lý hành động của người dùng trên threat."""
         res = mb.askquestion("Confirm", action.title() + " this threat? ")

         if res == "yes":
            selected_item = self.tree.selection()
            if selected_item:
               threat_data = self.tree.item(selected_item[0])["values"]
               threat_dict = {
                  "src_IP": threat_data[0],
                  "dst_IP": threat_data[1],
                  "protocol": threat_data[2],
                  "priority": threat_data[4],
                  "action_taken": threat_data[3],
                  "occur": threat_data[5],
                  "last_seen": threat_data[6],
               }
               result = self.controller.handle_threat_action(
                     threat_dict, action
               )
               print(f"From threat.py", {action, result})
               self.display_threats(self.page)
         else:
           pass


    def update_pagination(self):
        """Cập nhật thông tin phân trang."""
        total_threats = self.controller.get_total_threats()
        total_pages = (
            total_threats + self.per_page - 1
        ) // self.per_page
        self.page_label.config(text=f"Page {self.page}/{total_pages}")

        self.prev_button.config(state=tk.NORMAL if self.page > 1 else tk.DISABLED)
        self.next_button.config(
            state=tk.NORMAL if self.page < total_pages else tk.DISABLED
        )

    def prev_page(self):
        """Chuyển đến trang trước."""
        if self.page > 1:
            self.page -= 1
            self.display_threats(self.page)

    def next_page(self):
        """Chuyển đến trang sau."""
        total_threats = self.controller.get_total_threats()
        total_pages = (total_threats + self.per_page - 1) // self.per_page
        if self.page < total_pages:
            self.page += 1
            self.display_threats(self.page)