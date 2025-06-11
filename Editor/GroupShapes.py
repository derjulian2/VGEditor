
from PySide6.QtWidgets import QWidget, QDialog
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtCore import QPointF, QSizeF, QRectF

from Shapes import Shape
from Editor.Scene import Scene 
from Editor.Camera import Camera
from Editor.EditShape import EditShape

import Utility
#
# editor group-shapes class
#
# canvas-component that stores information and logic about grouping 
# together shapes to aggregate shapes
#
class GroupShapes:
    def __init__(self, editShape : EditShape):
        self.editShape : EditShape = editShape

        self.selected_shapes : list[Shape] = []

        self.active : bool = False
        self.enabled : bool = False
    
    def mousePressEvent(self, event : QMouseEvent) -> None:
        pass

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        pass

    def mouseMoveEvent(self, event : QMouseEvent) -> None:
        pass