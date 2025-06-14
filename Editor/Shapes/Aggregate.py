from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QPolygonF, QTransform

from PySide6.QtCore import Qt

import Utility
from Shape import Shape, findBoundingBoxShapes

#
# shape that consists of multiple shapes itself
#
# information about the child-shapes is preserved, functions more like a shape-list
# with it's own bounding-box
#
class AggregateShape(Shape):
    
    def __init__(self, shapes : list[Shape]) -> None:
        self.__shapes__ : list[Shape] = shapes
        super().__init__(findBoundingBoxShapes(self.__shapes__))

    def update(self) -> None:
        # fit all subshapes into shared-bounding-box
        for __shape__ in self.__shapes__:
            __shape__.update()
        # update painterpath
        self.__painterpath__.clear()
        for __shape__ in self.__shapes__:
            self.__painterpath__ = self.__painterpath__.united(__shape__.__painterpath__)

    def describeShape(self) -> QPolygonF:
        res : QPolygonF = QPolygonF()
        for __shape__ in self.__shapes__:
            res = res.united(__shape__.describeShape())
        return res