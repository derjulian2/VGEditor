#
# imports for basic vectormath utility
# and qt compatibility
#
from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QVector2D, QPainter, QColor, QPainterPath

from View import View
#
# base class for all other shapes
#
# every other shape should at least
# implement all functionality of 'Shape'
#
class Shape:
    def __init__(self,
                 bounding_box : QRectF, 
                 fill_color : QColor = QColor(255, 0, 0), 
                 border_color : QColor = QColor(0, 255, 0), 
                 border_width : float = 2):
        self.fill_color : QColor = fill_color
        self.border_color : QColor = border_color
        self.border_width : float = border_width
        self.bounding_box : QRectF = bounding_box

    def draw_bounding_box(self, painter : QPainter, view : View):
        painter.drawRect(QRectF(view.transform(self.bounding_box.topLeft()), self.bounding_box.size()))

    def draw(self, painter : QPainter, view : View):
        raise TypeError("cannot draw shape base class")
#
# rectangle shape
#
# defined by position and size vector2D
#
class Rectangle(Shape):
    def __init__(self, position : QVector2D, size : QVector2D):
        super().__init__(QRectF(position.x(), position.y(), size.x(), size.y()))
        self.pos = position
        self.dim = size

    def topLeft(self) -> QPointF:
        return QPointF(self.pos.x(), self.pos.y())
    
    def size(self) -> QSizeF:
        return QSizeF(self.dim.x(), self.dim.y())

    def draw(self, painter : QPainter, view : View):
        painter.fillRect(QRectF(view.transform(QPointF(self.pos.x(), self.pos.y())), QSizeF(self.dim.x(), self.dim.y())), self.fill_color)
#
# triangle shape
#
# defined by a set of three points
#
class Triangle(Shape):
    def __init__(self, vertices : list[QVector2D] ):
        super().__init__()
        if (len(vertices) != 3):
            raise AttributeError(vertices, "triangle must have exactly 3 vertices")
        self.vertices : list[QVector2D] = vertices

    def draw(self, painter : QPainter, view : View):
        print("Triangle")
#
# circle shape
#
# defined by a center-point and a radius-value
#
class Circle(Shape):
    def __init__(self, midpoint : QVector2D, radius : float):
        super().__init__(QRectF(midpoint.x() - radius, midpoint.y() - radius, 2 * radius, 2 * radius))
        self.midpoint = midpoint
        self.rad = radius

    def center(self) -> QPointF:
        return QPointF(self.midpoint.x(), self.midpoint.y())
    
    def radius(self) -> float:
        return self.rad

    def draw(self, painter : QPainter, view : View):
        path : QPainterPath = QPainterPath()
        path.addEllipse(view.transform(self.center()), self.rad, self.rad)
        painter.fillPath(path, self.fill_color)