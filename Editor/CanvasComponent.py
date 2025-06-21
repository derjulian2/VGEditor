
from PySide6.QtGui import QMouseEvent, QWheelEvent

#
# interface class for a component of the canvas
# controlling states and logic of a feature (like camera/adding shapes/editing shapes etc.)
#
class CanvasComponent:
    def __init__(self):
        self.enabled = False
        self.active  = False

    def enable(self) -> None:
        self.enabled = True

    def disable(self) -> None:
        self.enabled = False
        self.active = False 

    def mousePressEvent(self, event : QMouseEvent) -> None:
        pass

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        pass

    def mouseMoveEvent(self, event : QMouseEvent) -> None:
        pass

    def wheelEvent(self, event : QWheelEvent) -> None:
        pass