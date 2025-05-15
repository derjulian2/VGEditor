from Window import Window
from PySide6.QtWidgets import QApplication

import sys

if __name__ == "__main__":
    app : QApplication = QApplication(sys.argv)

    main_window : Window = Window(None)
    main_window.show()

    app.exec()