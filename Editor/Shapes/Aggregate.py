from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QPolygonF, QTransform

from PySide6.QtCore import Qt

import Utility
from Editor.Shapes.Shape import Shape, findBoundingBoxShapes

#
# shape that consists of multiple shapes itself
#
# information about the child-shapes is preserved, functions more like a shape-list
# with it's own bounding-box
#
class AggregateShape(Shape):
    
    def __init__(self, shapes : list[Shape]) -> None:
        # shapes need to be associated with a ratio of position and size of the bounding-box
        # to be able to transform the correctly later
        self.__shapes__ : list[tuple[Shape, QPointF, QSizeF]] = []
        super().__init__(findBoundingBoxShapes(shapes))
        self.__calc_ratios__(shapes)

    def update(self) -> None:
        # update and fit all subshapes into shared-bounding-box
        self.__fit_shapes_to_bounding_box__()
        for __shape__ in self.__shapes__:
            __shape__[0].update()
        # update painterpath
        self.__painterpath__.clear()
        for __shape__ in self.__shapes__:
            self.__painterpath__ = self.__painterpath__.united(__shape__[0].__painterpath__)

    def describeShape(self) -> QPolygonF:
        res : QPolygonF = QPolygonF()
        for __shape__ in self.__shapes__:
            res = res.united(__shape__[0].describeShape())
        return res
    
    def __calc_ratios__(self, shapes : list[Shape]) -> None:
        for shape in shapes:
            if (self.size.width() == 0):
                self.size = QSizeF(0.01, self.size.height())
            if (self.size.height() == 0):
                self.size = QSizeF(self.size.width(), 0.01)
            pos_ratio : QPointF = Utility.QPointFAbs(Utility.QPointFDivide(shape.topLeft - self.__true_topleft__(), Utility.toQPointF(self.size)))
            size_ratio : QSizeF = Utility.QSizeFAbs(Utility.QSizeFDivide(shape.size, self.size))
            self.__shapes__.append((shape, pos_ratio, size_ratio))

    def __fit_shapes_to_bounding_box__(self) -> None:
        # determine topleft and size of every shape
        # and adjust to new bounding-box size
        for __shape__ in self.__shapes__:
            __shape__[0].topLeft = self.__true_topleft__() + Utility.QPointFMultiply(__shape__[1], Utility.toQPointF(Utility.QSizeFAbs(self.size)))
            __shape__[0].size = Utility.QSizeFMultiply(__shape__[2], Utility.QSizeFAbs(self.size))