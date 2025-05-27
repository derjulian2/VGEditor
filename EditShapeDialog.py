
from PySide6.QtWidgets import (
    QWidget,    QHBoxLayout,    QVBoxLayout, 
    QLabel,     QSpinBox,       QDoubleSpinBox, 
    QDialog,    QPushButton
)

from PySide6.QtGui import QColor
#
# edit-shape-dialog class
#
# used to reconfigure attributes of existing shapes
#
class EditShapeDialog(QDialog):
    def __init__(self):
        pass