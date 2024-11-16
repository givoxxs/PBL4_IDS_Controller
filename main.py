from controllers.ids_controller import IDSController
from views.main_window import MainWindow
from config import settings

def main():
    controller = IDSController()
    view = MainWindow(controller)
    view.show_frame("dashboard")
    view.run()

if __name__ == "__main__":
    main()