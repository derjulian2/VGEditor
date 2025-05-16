#
# imports for basic vectormath utility
# and qt compatibility
#
from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QPolygonF

from math import sin, cos, radians

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
                 outline_color : QColor = QColor(0, 255, 0), 
                 outline_width : float = 2):
        self.fill_color : QColor = fill_color
        self.outline_color : QColor = outline_color
        self.outline_width : float = outline_width
        self.bounding_box : QRectF = bounding_box
        self.show_bounding_box : bool = False
        self.show_fill_body : bool = True
        self.__painterpath__ : QPainterPath = QPainterPath()

    def move(self, new_position : QPointF) -> None:
        self.bounding_box.setTopLeft(new_position)

    def resize(self, new_size : QSizeF) -> None:
        self.bounding_box.setSize(new_size)
    
    def draw(self, painter : QPainter, view : View) -> None:
        if (self.show_fill_body):
            painter.fillPath(self.__painterpath__, QBrush(self.fill_color))
        if (self.outline_width > 0):
            painter.setPen(QPen(self.outline_color, self.outline_width))
            painter.drawPath(self.__painterpath__)
        if (self.show_bounding_box):
            painter.setPen(QPen(QColor(0, 0, 255), 2.0))
            painter.drawRect(QRectF(view.transform(self.bounding_box.topLeft()), self.bounding_box.size()))

#
# rectangle shape
#
# defined by position and size vector2D
#
class Rectangle(Shape):
    def __init__(self, position : QPointF, size : QSizeF):
        super().__init__(QRectF(position.x(), position.y(), size.width(), size.height()))
        self.rect : QRectF = QRectF(position, size)

    def draw(self, painter : QPainter, view : View) -> None:
        self.__painterpath__.clear()
        self.__painterpath__.addRect(QRectF(view.transform(self.rect.topLeft()), self.rect.size()))
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

    def draw(self, painter : QPainter, view : View):
        self.__painterpath__.clear()
        self.__painterpath__.addEllipse(view.transform(self.midpoint), self.radius, self.radius)
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

    def draw(self, painter : QPainter, view : View):
        self.__painterpath__.clear()
        
        transformed_polygon : QPolygonF = QPolygonF()
        for point in self.polygon.toList():
            transformed_polygon.append(view.transform(point))

        self.__painterpath__.addPolygon(transformed_polygon)
        super().draw(painter, view)