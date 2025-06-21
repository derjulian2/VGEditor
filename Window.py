from PySide6.QtCore import QSize, QPointF, QSizeF

from PySide6.QtGui import (
    QColor,     QAction,    QIcon,    QCloseEvent
)

from PySide6.QtWidgets import (
    QFrame,         QMenuBar,       QToolBar,
    QVBoxLayout,    QFileDialog,    QMessageBox,
    QMainWindow,    QMessageBox,    QMenu,
)

from Editor.Shapes.Primitives import Rectangle, Ellipse, Star, Circle
from Editor.Canvas import Canvas, EditorState
from Editor.Scene import exampleScene1, exampleScene2, exampleScene3
#
# window class
#
# shows the actual editor-screen of the vector-graphics-editor
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
        file_export_action : QAction = file_button.addAction(QIcon(""), "Export to .svg")
        file_close_action : QAction = file_button.addAction(QIcon("icons/door--arrow.png"), "Close")

        add_rect_action : QAction = self.addAction(QIcon(""), "add Rectangle")
        add_ellipse_action : QAction = self.addAction(QIcon(""), "add Ellipse")
        add_circ_action : QAction = self.addAction(QIcon(""), "add Circle")
        add_star_action : QAction = self.addAction(QIcon(""), "add Star")

        
        help_information_action : QAction = help_button.addAction(QIcon("icons/information.png"), "About")
        self.move_mode_action : QAction = self.toolbar.addAction(QIcon("icons/arrow-move.png"), "Move Scene")
        self.group_mode_action : QAction = self.toolbar.addAction(QIcon(""), "Group Shapes")
        self.move_mode_action.setCheckable(True)
        self.group_mode_action.setCheckable(True)
        
        
        file_new_action.triggered.connect(self.action_new)
        file_export_action.triggered.connect(self.action_export)
        file_close_action.triggered.connect(self.close)
        help_information_action.triggered.connect(self.action_info)
        example_1_action.triggered.connect(self.action_example_1)
        example_2_action.triggered.connect(self.action_example_2)
        example_3_action.triggered.connect(self.action_example_3)
        self.move_mode_action.triggered.connect(self.action_move)
        self.group_mode_action.triggered.connect(self.action_group)

        add_rect_action.triggered.connect(self.action_add_rect)
        add_ellipse_action.triggered.connect(self.action_add_ellipse)
        add_circ_action.triggered.connect(self.action_add_circ)
        add_star_action.triggered.connect(self.action_add_star)

        self.toolbar.addActions([file_new_action, 
                                 add_rect_action,
                                 add_ellipse_action,
                                 add_circ_action,
                                 add_star_action,
                                 self.move_mode_action, 
                                 file_close_action, 
                                 help_information_action])

    def action_new(self):
        if QMessageBox.question(self, "create new scene?", "unsaved progress will be lost") == QMessageBox.Yes:
            self.canvas.clear()

    def action_export(self):
        file_name, selected_filter = QFileDialog.getSaveFileName(self, "Select Export Path", "","SVG Files (*.svg)")
        if (len(file_name)):
            self.canvas.exportSceneToSVG(file_name, "VGEditor Scene", "placeholder description")

    def action_move(self, state : bool):
        if (state):
            self.canvas.setState(EditorState.SCROLL_CAMERA)
        else:
            self.canvas.setState(EditorState.EDIT)

    def action_group(self, state : bool):
        if (state):
            self.canvas.setState(EditorState.GROUP)
        else:
            self.canvas.setState(EditorState.EDIT)

    def action_add_rect(self):
        self.move_mode_action.setChecked(False)
        self.canvas.setState(EditorState.NEW)
        self.canvas.newShape.makeNewShape(Rectangle(QPointF(0.0, 0.0), QSizeF(0.0, 0.0)))

    def action_add_ellipse(self):
        self.move_mode_action.setChecked(False)
        self.canvas.setState(EditorState.NEW)
        self.canvas.newShape.makeNewShape(Ellipse(QPointF(0.0, 0.0), QSizeF(0.0, 0.0)))

    def action_add_circ(self):
        self.move_mode_action.setChecked(False)
        self.canvas.setState(EditorState.NEW)
        self.canvas.newShape.makeNewShape(Circle(QPointF(0.0, 0.0), 0.0))

    def action_add_star(self):
        self.move_mode_action.setChecked(False)
        self.canvas.setState(EditorState.NEW)
        self.canvas.newShape.makeNewShape(Star(QPointF(0.0, 0.0), QSizeF(0.0, 0.0), QSizeF(0.0, 0.0), 3))

    def action_example_1(self):
        self.canvas.clear()
        exampleScene1(self.canvas.scene)

    def action_example_2(self):
        self.canvas.clear()
        exampleScene2(self.canvas.scene)

    def action_example_3(self):
        self.canvas.clear()
        exampleScene3(self.canvas.scene)
    
    def closeEvent(self, event : QCloseEvent):
        if (QMessageBox.question(self, "Really close?", "Progress may be unsaved", QMessageBox.Yes, QMessageBox.No) == QMessageBox.Yes):
            event.accept()
        else:
            event.ignore()

    def action_info(self):
         QMessageBox.information(self, "Information", 
                                 "EiS vector-graphics-editor SoSe 2025 JGU Mainz\n\n" \
                                 "by group 3A\n\n" \
                                 "This app uses the fugue-icon-set by Yusuke Kamiyamane downloaded from https://p.yusukekamiyamane.com/ "
                                 "in May 2025 licensed under a Creative Commons Attribution 3.0 License", QMessageBox.Close)