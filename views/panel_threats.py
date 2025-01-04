import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb
from controllers.ids_controller import IDSController
import logging
import time
import asyncio
from threading import Thread

logger = logging.getLogger(__name__)

class PanelThreats(tk.Frame):
    def __init__(self, parent, controller: IDSController):
        super().__init__(parent)
        self.controller = controller
        self.page = 1
        self.per_page = 10
        self.default_max_priority = 3  # set the default value here
        self.create_widgets()
        self.display_threats()

    def create_widgets(self):
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
        logger.info("Loading panel threats")
        for item in self.tree.get_children():
            self.tree.delete(item)

        offset = (page - 1) * self.per_page
        threats = self.controller.get_threats(limit=self.per_page, offset=offset, priority=self.default_max_priority)
        self.page = page
        self.update_pagination()

        for threat in threats:
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

    def handle_threat_action(self, action: str):
        res = mb.askquestion("Confirm", f"{action.title()} this threat?")
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

                self.show_loading()
                # Run in a separate thread
                Thread(
                    target=self.run_async_action,
                    args=(action, threat_dict),
                    daemon=True,
                ).start()

    def run_async_action(self, action, threat_dict):
        """Wrapper to run the asyncio event loop."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(self._process_threat_action(action, threat_dict))
        loop.close()

        # Ensure loading screen is hidden in the main thread
        self.after(0, self.hide_loading)  # Hide loading window
        # Ensure threats are displayed in the main thread after processing
        self.after(0, self.display_threats, self.page)

    async def _process_threat_action(self, action: str, threat_dict):
        result = self.controller.handle_threat_action(threat_dict, action)
        logger.info(f"Action {action}: {result}")
        return result

    def show_loading(self):
        self.loading_window = tk.Toplevel(self)
        self.loading_window.title("Loading...")
        self.loading_window.resizable(False, False)

        label = tk.Label(self.loading_window, text="Please wait...", font=("Helvetica", 12))
        label.pack(padx=20, pady=20)

    def hide_loading(self):
        """Close the loading window."""
        self.loading_window.destroy()
    def update_pagination(self):
        total_threats = self.controller.get_total_threats()
        total_pages = (total_threats + self.per_page - 1) // self.per_page
        self.page_label.config(text=f"Page {self.page}/{total_pages}")

        self.prev_button.config(state=tk.NORMAL if self.page > 1 else tk.DISABLED)
        self.next_button.config(
            state=tk.NORMAL if self.page < total_pages else tk.DISABLED
        )

    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            self.display_threats(self.page)

    def next_page(self):
        total_threats = self.controller.get_total_threats()
        total_pages = (total_threats + self.per_page - 1) // self.per_page
        if self.page < total_pages:
            self.page += 1
            self.display_threats(self.page)