#
# imports for basic vectormath utility
# and qt compatibility
#
from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QPolygonF

from math import sin, cos, radians

from View import View

import Utility
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
                 outline_color : QColor = QColor(0, 255, 0), 
                 outline_width : float = 2):
        self.fillColor : QColor = fill_color
        self.outlineColor : QColor = outline_color
        self.outlineWidth : float = outline_width
        self.boundingBox : QRectF = bounding_box
        self.showBoundingBox : bool = False
        self.showFillBody : bool = True
        self.__painterpath__ : QPainterPath = QPainterPath()

    def move(self, pos : QPointF) -> None:
        self.boundingBox.setTopLeft(pos)

    def resize(self, size : QSizeF) -> None:
        self.boundingBox.setSize(size)
    
    def draw(self, painter : QPainter, view : View) -> None:
        if (self.showFillBody):
            painter.fillPath(self.__painterpath__, QBrush(self.fillColor))
        if (self.outlineWidth > 0):
            painter.setPen(QPen(self.outlineColor, self.outlineWidth))
            painter.drawPath(self.__painterpath__)
        if (self.showBoundingBox):
            painter.setPen(QPen(QColor(0, 0, 255), 2.0))
            painter.drawRect(QRectF(view.transformPoint(self.boundingBox.topLeft()), 
                                    view.transformSize(self.boundingBox.size())))

#
# rectangle shape
#
# defined by position and size vector2D
#
class Rectangle(Shape):
    def __init__(self, position : QPointF, size : QSizeF):
        super().__init__(QRectF(position.x(), position.y(), size.width(), size.height()))

    def draw(self, painter : QPainter, view : View) -> None:
        self.__painterpath__.clear()
        self.__painterpath__.addRect(QRectF(view.transformPoint(self.boundingBox.topLeft()), 
                                            view.transformSize(self.boundingBox.size())))
        super().draw(painter, view)
#
# circle shape
#
# defined by a center-point and a radius-value
#
class Circle(Shape):
    def __init__(self, midpoint : QPointF, radius : float):
        super().__init__(QRectF(midpoint.x() - radius, midpoint.y() - radius, 2 * radius, 2 * radius))
        self.midpoint : QPointF = midpoint
        self.radius : float = radius

    def move(self, pos : QPointF):
        super().move(pos)
        self.midpoint = pos + QPointF(self.radius, self.radius)

    def resize(self, size : QSizeF):
        super().resize(QSizeF(size.width(), size.width()))
        self.midpoint = self.boundingBox.topLeft() + 0.5 * QPointF(size.width(), size.width())
        self.radius = 0.5 * size.width()

    def draw(self, painter : QPainter, view : View):
        self.__painterpath__.clear()
        radius_proj : QSizeF = view.transformSize(QSizeF(self.radius, self.radius))
        self.__painterpath__.addEllipse(view.transformPoint(self.midpoint), 
                                        radius_proj.width(), radius_proj.width())
        super().draw(painter, view)
#
# star shape
#
# defined by a center-point, an outer and inner radius and the number of edges
#
class Star(Shape):
    def __init__(self, midpoint : QPointF, radius : float, num_edges : int):
        if (num_edges < 3):
            raise AttributeError("star must have at least 3 edges")
        super().__init__(QRectF(midpoint.x() - radius, midpoint.y() - radius, 2 * radius, 2 * radius))
        self.midpoint = midpoint
        self.radius = radius
        self.inner_radius = radius * 0.4
        self.num_edges = num_edges
        self.polygon : QPolygonF = QPolygonF()
        self.__calculate_edges__()

    def __calculate_edges__(self):
        points : list[QPointF] = []

        angle : int = 0
        inner_angle_offset : int = int(180/self.num_edges)
        while (angle < 360):
            points.append(self.midpoint + QPointF(self.radius * cos(radians(angle)), 
                                                  self.radius * sin(radians(angle))))
            points.append(self.midpoint + QPointF(self.inner_radius * cos(radians(angle + inner_angle_offset)), 
                                                  self.inner_radius * sin(radians(angle + inner_angle_offset))))
            angle += int(360/self.num_edges)

        self.polygon.clear()
        for point in points:
            self.polygon.append(point)

    def move(self, pos : QPointF):
        super().move(pos)
        self.midpoint = pos + QPointF(self.radius, self.radius)
        self.__calculate_edges__()

    def resize(self, size : QSizeF):
        super().resize(QSizeF(size.width(), size.width()))
        self.midpoint = self.boundingBox.topLeft() + 0.5 * QPointF(size.width(), size.width())
        self.radius = 0.5 * size.width()
        self.__calculate_edges__()

    def draw(self, painter : QPainter, view : View):
        self.__painterpath__.clear()
        
        transformed_polygon : QPolygonF = QPolygonF()
        for point in self.polygon.toList():
            transformed_polygon.append(view.transformPoint(point))

        self.__painterpath__.addPolygon(transformed_polygon)
        super().draw(painter, view)