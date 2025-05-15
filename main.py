from PySide6.QtCore import QSize, QPoint

from PySide6.QtGui import (
    QImage,         QPen,           QPainter,
    QColor,         QAction,        QIcon,
    QPaintEvent,    QMouseEvent,    QVector2D
)

from PySide6.QtWidgets import (
    QApplication,   QMenuBar,       QToolBar,
    QWidget,        QFileDialog,    QMessageBox,
    QMainWindow,    QMessageBox,    QMenu
)

from Shapes import Rectangle, Circle
from Canvas import Canvas
             
# Klasse für GUI Fenster
class Window(QMainWindow):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)

        self.canvas : Canvas = Canvas(parent, QSize(640, 480))
        self.setCentralWidget(self.canvas)

        self.testrect : Rectangle = Rectangle(QVector2D(50, 50), QVector2D(50, 50))
        self.testcirc : Circle = Circle(QVector2D(100, 100), 75)
        self.testcirc.fill_color = QColor(0, 255, 0)

        self.canvas.scene.attach_objects([self.testcirc, self.testrect])



        self.menu_bar : QMenuBar = self.menuBar()

        file_button : QMenu = self.menu_bar.addMenu("File")
        help_button : QMenu = self.menu_bar.addMenu("Help")
        
        file_open_action : QAction = file_button.addAction(QIcon("icons/folder-horizontal-open.png"), "Open")
        file_save_action : QAction = file_button.addAction(QIcon("icons/disk.png"), "Save as")
        file_close_action : QAction = file_button.addAction(QIcon("icons/door--arrow.png"), "Close")
        help_information_action : QAction = help_button.addAction(QIcon("icons/information.png"), "About")
        
        file_open_action.triggered.connect(self.action_open)
        file_save_action.triggered.connect(self.action_save)
        file_close_action.triggered.connect(self.action_close)
        help_information_action.triggered.connect(self.action_info)

        self.toolbar : QToolBar = self.addToolBar("Tools")
        self.toolbar.setIconSize(QSize(16, 16))

        clear_canvas_action : QAction = self.toolbar.addAction("Clear")
        clear_canvas_action.triggered.connect(self.action_clear)

        self.toolbar.addActions([file_open_action, file_save_action, file_close_action, help_information_action])
    
    # File-Operationen wie in d) gefordert
    # Raussuchen einer Bilddatei via QFileDialog
    def action_open(self):
        pass
        file_name, selected_filter = QFileDialog.getOpenFileName(self, "Choose a File", "", "Images (*.png *.xpm *.jpg)")
        #if (file_name):
        #    self.paint_area.load_image(file_name)

    # Raussuchen eines Speicherplatzes für aktuelles Bild via QFileDialog
    def action_save(self):
        pass
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Choose a Location", "", "Images (*.png *.xpm *.jpg)")
        #if (file_name):
        #    self.paint_area.save_image(file_name)

    # Beenden des Programms mit Sicherheitsabfrage
    def action_close(self):
        if (QMessageBox.question(self, "Really close?", "Progress may be unsaved", QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes):
            self.close()

    # Leinwand leeren
    def action_clear(self):
        self.canvas.clear()
        
    # Informationen über das Programm
    def action_info(self):
         QMessageBox.information(self, "Information", 
                                 "EiS assignment 2 SoSe 2025 JGU Mainz\n\n" \
                                 "Übung 3 Abgabegruppe A\n\n" \
                                 "This app uses the fugue-icon-set by Yusuke Kamiyamane downloaded from https://p.yusukekamiyamane.com/ "
                                 "in May 2025 licensed under a Creative Commons Attribution 3.0 License", QMessageBox.Close)

import sys
# Generische Qt-Main Funktion zum aufrufen der GUI
if __name__ == "__main__":
    app : QApplication = QApplication(sys.argv)

    main_window : Window = Window(None)
    main_window.show()

    app.exec()