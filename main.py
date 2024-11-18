from controllers.ids_controller import IDSController
from views.main_window import MainWindow
from config import settings, logging_config
import logging

def main():
    logging_config.setup_logging(log_level=logging.DEBUG)
    controller = IDSController()
    view = MainWindow(controller)
    view.run()

if __name__ == "__main__":
    main()