from controllers.ids_controller import IDSController
from views.main_window import MainWindow
from config import settings, logging_config
import logging
import tkinter as tk

def main():
    logging_config.setup_logging(log_level=logging.DEBUG)
    root = tk.Tk()
    controller = IDSController(root)
    view = MainWindow(root, controller)
    view.pack(fill="both", expand=True)
    view.run()

if __name__ == "__main__":
    main()