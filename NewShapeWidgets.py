
from PySide6.QtWidgets import (
    QWidget,    QHBoxLayout,    QVBoxLayout, 
    QLabel,     QSpinBox,       QDoubleSpinBox, 
    QDialog,    QPushButton
)

from PySide6.QtGui import QColor

from Shapes import Shape, Star
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
    def __init__(self, label : str, shape : Shape):
        super().__init__()
        self.shape : Shape = shape

        self.dialogLayout : QVBoxLayout = QVBoxLayout()
        self.label : QLabel = QLabel(label)

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

        if (isinstance(self.shape, Star)):
            self.dialogLayout.addWidget(self.innerRadius)
            self.dialogLayout.addWidget(self.numEdges)

        self.buttonDone.clicked.connect(self.accept)
        self.buttonCancel.clicked.connect(self.reject)

        self.exitButtonLayout.addWidget(self.buttonDone)
        self.exitButtonLayout.addWidget(self.buttonCancel)

        self.dialogLayout.addWidget(self.fillColor)
        self.dialogLayout.addWidget(self.outlineColor)
        self.dialogLayout.addWidget(self.outlineWidth)
        self.dialogLayout.addLayout(self.exitButtonLayout)
        self.setLayout(self.dialogLayout)
