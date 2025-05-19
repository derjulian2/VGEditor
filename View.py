from PySide6.QtCore import QPointF, QSizeF
from PySide6.QtGui import QTransform

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
    def __init__(self, viewportSize : QSizeF, viewportArea : QSizeF, topLeft : QPointF = QPointF(0, 0)):
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