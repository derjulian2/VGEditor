from PySide6.QtCore import QPointF, QSizeF
from PySide6.QtGui import QTransform, QMouseEvent, QWheelEvent
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt

import Utility
#
# view class
#
# defines what part of a canvas should be displayed
# when Scene.draw() is called
#
# View.transform must be connected to the corresponding QPainter to be effective
#
class View:
    def __init__(self, viewportSize : QSizeF, viewportArea : QSizeF, topLeft : QPointF = QPointF(0, 0)) -> None:
        self.topLeft : QPointF = topLeft
        self.zoomFactor : float = 1.0
        self.viewportSize : QSizeF = viewportSize
        self.viewportArea : QSizeF = viewportArea
        self.transform : QTransform = QTransform()

    def zoom(self, zoomFactor : float) -> None:
        self.viewportArea = Utility.toQSizeF(Utility.toQVector2D(self.viewportSize) * zoomFactor)

    def updateTransform(self) -> None:
        self.transform.reset()
        self.transform.translate(0.5 * self.viewportSize.width(), 0.5 * self.viewportSize.height())
        self.transform.scale(self.zoomFactor, self.zoomFactor)
        self.transform.translate(-self.topLeft.x(), -self.topLeft.y())

    def mapToScreen(self, point : QPointF) -> QPointF:
        self.updateTransform()
        return self.transform.map(point)
    
    def mapToWorld(self, point : QPointF) -> QPointF:
        self.updateTransform()
        return self.transform.inverted()[0].map(point)

from Editor.CanvasComponent import CanvasComponent
#
# editor-camera class
#
# stores information and logic about viewing the canvas through a view
#
class Camera(CanvasComponent):
    def __init__(self, parent : QWidget, viewportSize : QSizeF) -> None:
        super().__init__()
        self.view : View = View(viewportSize, viewportSize)
        self.parent : QWidget = parent

        self.anchorPoint : QPointF = QPointF()
        self.viewAnchorPoint : QPointF = QPointF()
        self.dragging : bool = False

    def disable(self) -> None:
        super().disable()
        self.dragging = False 

    def mousePressEvent(self, event : QMouseEvent) -> None:
        if (self.enabled and not self.active):
            self.anchorPoint = Utility.toQPointF(event.pos())
            self.viewAnchorPoint = self.view.topLeft
            self.dragging = True
            self.parent.setCursor(Qt.CursorShape.SizeAllCursor)
            self.active = True

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        if (self.enabled and self.active):
            self.dragging = False
            self.active = False
            self.parent.setCursor(Qt.CursorShape.ArrowCursor)
    
    def mouseMoveEvent(self, event : QMouseEvent) -> None:
        if (self.enabled and self.active):
            if (self.dragging):
                self.view.topLeft = self.viewAnchorPoint + self.view.mapToWorld(self.anchorPoint) - self.view.mapToWorld(Utility.toQPointF(event.pos()))

    def wheelEvent(self, event : QWheelEvent) -> None:
        if (self.enabled and self.active):
            if (event.angleDelta().y() > 0):
                self.zoomFactor = Utility.Clamp(self.zoomFactor + 0.05, 0.5, 1.75)
            else:
                self.zoomFactor = Utility.Clamp(self.zoomFactor - 0.05, 0.5, 1.75)
            self.view.zoom(self.zoomFactor)