from controllers.ids_controller import IDSController
from views.main_window import MainWindow
from config import settings, logging

def main():
    logging.setup_logging()
    controller = IDSController()
    view = MainWindow(controller)
    view.show_frame("dashboard")
    view.run()

if __name__ == "__main__":
    main()