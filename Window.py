from PySide6.QtCore import QSize, QPointF, QSizeF

from PySide6.QtGui import (
    QImage,         QPen,           QPainter,
    QColor,         QAction,        QIcon,
    QPaintEvent,    QMouseEvent,    QCloseEvent
)

from PySide6.QtWidgets import (
    QFrame,         QMenuBar,       QToolBar,
    QVBoxLayout,    QFileDialog,    QMessageBox,
    QMainWindow,    QMessageBox,    QMenu
)

from Shapes import Rectangle, Circle, Star
from Canvas import Canvas           
#
# window class
#
# will show the actual vector-graphics-editor gui
#
class Window(QMainWindow):
    def __init__(self, parent: QMainWindow):
        super().__init__(parent)

        self.frame : QFrame = QFrame(self)
        self.setCentralWidget(self.frame)
        self.layout : QVBoxLayout = QVBoxLayout(self.frame)
        self.frame.setLayout(self.layout)

        self.canvas : Canvas = Canvas(parent, QSize(1080, 720))
        self.layout.addWidget(self.canvas)

        self.menu_bar : QMenuBar = self.menuBar()
        self.toolbar : QToolBar = self.addToolBar("Tools")
        self.toolbar.setIconSize(QSize(16, 16))

        file_button : QMenu = self.menu_bar.addMenu("File")
        help_button : QMenu = self.menu_bar.addMenu("Help")

        examples_button : QMenu = file_button.addMenu("Examples")

        example_1_action : QAction = examples_button.addAction("Example 1")
        example_2_action : QAction = examples_button.addAction("Example 2")
        example_3_action : QAction = examples_button.addAction("Example 3")
        
        file_new_action : QAction = file_button.addAction(QIcon("icons/blue-document--plus"), "New Scene")
        file_close_action : QAction = file_button.addAction(QIcon("icons/door--arrow.png"), "Close")
        help_information_action : QAction = help_button.addAction(QIcon("icons/information.png"), "About")
        move_mode_action : QAction = self.toolbar.addAction(QIcon("icons/arrow-move.png"), "Move Scene")
        move_mode_action.setCheckable(True)
        
        file_new_action.triggered.connect(self.action_new)
        file_close_action.triggered.connect(self.action_close)
        help_information_action.triggered.connect(self.action_info)
        example_1_action.triggered.connect(self.action_example_1)
        example_2_action.triggered.connect(self.action_example_2)
        example_3_action.triggered.connect(self.action_example_3)
        move_mode_action.triggered.connect(self.action_move)

        self.toolbar.addActions([file_new_action, move_mode_action, file_close_action, help_information_action])

    def action_new(self):
        if QMessageBox.question(self, "create new scene?", "unsaved progress will be lost") == QMessageBox.Yes:
            self.canvas.clear()

    def action_move(self, state : bool):
        self.canvas.setMoveMode(state)

    def action_example_1(self):
        self.canvas.clear()

        rectangle_1 : Rectangle = Rectangle(QPointF(100.0, 100.0), QSizeF(100.0, 100.0))
        rectangle_1.show_fill_body = False
        rectangle_1.outline_color = QColor(0, 0, 255)
        rectangle_1.outline_width = 2.0

        circle_1 : Circle = Circle(QPointF(150.0, 150.0), 50.0)
        circle_1.show_fill_body = False
        circle_1.outline_color = QColor(255, 0, 0)
        circle_1.outline_width = 2.0

        self.canvas.scene.attach_objects([rectangle_1, circle_1])

    def action_example_2(self):
        self.canvas.clear()

        padding : float = 5.0
        rectangles : list[Rectangle] = [Rectangle(QPointF(200.0 + padding, 100.0), QSizeF(100.0, 100.0)),
                                        Rectangle(QPointF(300.0 + 2 * padding, 100.0), QSizeF(100.0, 100.0)),
                                        Rectangle(QPointF(100.0, 200.0 + padding), QSizeF(100.0, 100.0)),
                                        Rectangle(QPointF(200.0 + padding, 300.0 + 2 * padding), QSizeF(100.0, 100.0)),
                                        Rectangle(QPointF(300.0 + 2 * padding, 300.0 + 2 * padding), QSizeF(100.0, 100.0)),
                                        Rectangle(QPointF(400.0 + 3 * padding, 200.0 + padding), QSizeF(100.0, 100.0))]

        circles : list[Circle] = [Circle(QPointF(150.0, 150.0), 50.0), 
                                  Circle(QPointF(450.0 + 3 * padding, 150.0), 50.0), 
                                  Circle(QPointF(450.0 + 3 * padding, 350.0 + 2 * padding), 50.0), 
                                  Circle(QPointF(150.0, 350.0 + 2 * padding), 50.0)]

        for rect in rectangles:
            rect.fill_color = QColor(0, 0, 255)
            rect.outline_color = QColor(255, 0, 0)
            rect.outline_width = 2.0

        for circ in circles:
            circ.fill_color = QColor(255, 0, 0)
            circ.outline_color = QColor(0, 0, 255)
            circ.outline_width = 2.0

        self.canvas.scene.attach_objects(rectangles)
        self.canvas.scene.attach_objects(circles)

    def action_example_3(self):
        self.canvas.clear()

        star_1 : Star = Star(QPointF(150.0, 150.0), 150.0, 6)

        self.canvas.scene.attach_objects([star_1])

    def action_close(self):
        if (QMessageBox.question(self, "Really close?", "Progress may be unsaved", QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes):
            self.close()
    
    def closeEvent(self, event : QCloseEvent):
        if (QMessageBox.question(self, "Really close?", "Progress may be unsaved", QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes):
            self.close()
        else:
            event.ignore()

    def action_info(self):
         QMessageBox.information(self, "Information", 
                                 "EiS vector-graphics-editor SoSe 2025 JGU Mainz\n\n" \
                                 "by group 3A\n\n" \
                                 "This app uses the fugue-icon-set by Yusuke Kamiyamane downloaded from https://p.yusukekamiyamane.com/ "
                                 "in May 2025 licensed under a Creative Commons Attribution 3.0 License", QMessageBox.Close)