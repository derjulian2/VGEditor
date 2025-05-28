
from PySide6.QtWidgets import (
    QWidget,    QHBoxLayout,    QVBoxLayout, 
    QLabel,     QSpinBox,       QDoubleSpinBox, 
    QDialog,    QPushButton
)
from PySide6.QtCore import QPointF, QSizeF
from PySide6.QtGui import QColor, QPainter, QMouseEvent
from PySide6.QtCore import Qt
from Shapes import Shape, Rectangle, Ellipse, Circle, Star
from Editor.Camera import Camera
from Editor.Scene import Scene
import Utility
#
# labeled spinbox
#
# bundles a label and a spinbox into one widget
#
class LabeledSpinBox(QWidget):
    def __init__(self, parent : QWidget, label : str):
        super().__init__(parent)
        self.layout : QHBoxLayout = QHBoxLayout()

        self.label : QLabel = QLabel(label, self)
        self.spinbox : QSpinBox = QSpinBox()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.setLayout(self.layout)
#
# labeled doublespinbox
#
# bundles a label and a doublespinbox into one widget
#
class LabeledDoubleSpinBox(QWidget):
    def __init__(self, parent : QWidget, label : str):
        super().__init__(parent)
        self.layout : QHBoxLayout = QHBoxLayout()

        self.label : QLabel = QLabel(label, self)
        self.spinbox : QDoubleSpinBox = QDoubleSpinBox()

        self.layout.addWidget(self.label)
        self.layout.addWidget(self.spinbox)
        self.setLayout(self.layout)
#
# rgb-colorspinbox widget
#
# bundles a label and three spinboxes ranging from 0-255 into one widget
#
class RGBColorSpinBox(QWidget):
    def __init__(self, parent : QWidget, label : str):
        super().__init__(parent)

        self.spinBoxLayout : QHBoxLayout = QHBoxLayout()

        self.label : QLabel = QLabel(label, self)
        self.R : QSpinBox = QSpinBox(self)
        self.G : QSpinBox = QSpinBox(self)
        self.B : QSpinBox = QSpinBox(self)
        self.R.setRange(0, 255)
        self.G.setRange(0, 255)
        self.B.setRange(0, 255)

        self.spinBoxLayout.addWidget(self.label)
        self.spinBoxLayout.addWidget(self.R)
        self.spinBoxLayout.addWidget(self.G)
        self.spinBoxLayout.addWidget(self.B)
        self.setLayout(self.spinBoxLayout)

    def getColor(self) -> QColor:
        return QColor(self.R.value(), self.B.value(), self.G.value())
        
#
# new-shape-dialog
#
# used to configure attributes of newly generated shapes
# that cannot be set using the editor directly (e.g. through mouse-movements)
#
class NewShapeDialog(QDialog):
    def __init__(self, shape : Shape):
        super().__init__()
        self.shape : Shape = shape

        self.dialogLayout : QVBoxLayout = QVBoxLayout()
        label_str : str = "configure new "
        if (isinstance(shape, Rectangle)):
            label_str += "Rectangle"
        elif (isinstance(shape, Circle)): # circle before ellipse because all circles are also ellipses
            label_str += "Circle"
        elif (isinstance(shape, Ellipse)):
            label_str += "Ellipse"
        elif (isinstance(shape, Star)):
            label_str += "Star"
        self.label : QLabel = QLabel(label_str)

        self.exitButtonLayout : QHBoxLayout = QHBoxLayout()
        self.buttonDone : QPushButton = QPushButton("Done", self)
        self.buttonCancel : QPushButton = QPushButton("Cancel", self)

        if (isinstance(self.shape, Star)):
            self.innerRadius : LabeledDoubleSpinBox = LabeledDoubleSpinBox(self, "Star-Inner-Radius:")
            self.numEdges : LabeledSpinBox = LabeledSpinBox(self, "Star number of outer-vertices:")
            self.innerRadius.spinbox.setRange(10.0, 512.0)
            self.numEdges.spinbox.setRange(3, 64)

        self.fillColor : RGBColorSpinBox = RGBColorSpinBox(self, "Fill-Color:")
        self.outlineColor : RGBColorSpinBox = RGBColorSpinBox(self, "Outline-Color:")
        self.outlineWidth : LabeledDoubleSpinBox = LabeledDoubleSpinBox(self, "Outline-Width:")

        self.buttonDone.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)

        self.exitButtonLayout.addWidget(self.buttonDone)
        self.exitButtonLayout.addWidget(self.buttonCancel)

        self.dialogLayout.addWidget(self.label)
        if (isinstance(self.shape, Star)):
            self.dialogLayout.addWidget(self.innerRadius)
            self.dialogLayout.addWidget(self.numEdges)
        self.dialogLayout.addWidget(self.fillColor)
        self.dialogLayout.addWidget(self.outlineColor)
        self.dialogLayout.addWidget(self.outlineWidth)
        self.dialogLayout.addLayout(self.exitButtonLayout)
        self.setLayout(self.dialogLayout)

    def configureShape(self) -> None:
        if (self.result()):
            self.shape.fillColor = self.fillColor.getColor()
            self.shape.outlineColor = self.outlineColor.getColor()
            self.shape.outlineWidth = self.outlineWidth.spinbox.value()
            if (isinstance(self.shape, Star)):
                self.shape.numOuterVertices = self.numEdges.spinbox.value()
                self.shape.innerSize = QSizeF(self.innerRadius.spinbox.value(), self.innerRadius.spinbox.value())

#
# editor-new-shape class
#
# stores information and logic about when a new shape is created
#
class NewShape:
    def __init__(self, parent : QWidget, camera : Camera, scene : Scene):
        self.parent : QWidget = parent
        self.camera : Camera = camera
        self.scene : Scene = scene

        self.shape : Shape = None
        self.anchor_point : QPointF = None
        self.dragging : bool = False

        self.active : bool = False
        self.enabled : bool = False

    def makeNewShape(self, shape : Shape) -> None:
        if (self.enabled and not self.active):
            dialog : NewShapeDialog = NewShapeDialog(shape)
            dialog.exec()
            dialog.configureShape()

            if (dialog.result()):
                self.shape = shape
                self.scene.attach_object(self.shape)
                self.active = True

    def mousePressEvent(self, event : QMouseEvent) -> None:
        if (self.enabled and self.active):
            self.parent.setCursor(Qt.CursorShape.CrossCursor)
            self.anchor_point = self.camera.mapToWorld(Utility.toQPointF(event.pos()))
            self.dragging = True

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        if (self.enabled and self.active):
            self.parent.setCursor(Qt.CursorShape.ArrowCursor)
            self.dragging = False
            self.active = False
    
    def mouseMoveEvent(self, event : QMouseEvent) -> None:
        if (self.enabled and self.active):
            if (self.dragging):
                delta : QPointF = self.camera.mapToWorld(Utility.toQPointF(event.pos())) - self.anchor_point
                self.shape.center = self.anchor_point + 0.5 * delta
                self.shape.size = Utility.toQSizeF(delta)

