from controllers.ids_controller import IDSController
from services.alert_service import AlertService
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
    view.run()  # Call view.run() to start setup, before root.mainloop()
    root.mainloop()  # Start the Tkinter main loop after setup


if __name__ == "__main__":
    main()