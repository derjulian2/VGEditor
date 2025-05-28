#
# imports for basic vectormath utility
# and qt compatibility
#
from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QPolygonF

from PySide6.QtCore import Qt

from math import sin, cos, radians

import Utility
#
# base class for all other shapes
#
# every other shape should at least
# implement all functionality of 'Shape'
#
class Shape:

    boundingBoxColor : QColor = QColor(16, 227, 206)
    boundingBoxWidth : float = 2.5

    def __init__(self,
                 bounding_box : QRectF, 
                 fill_color : QColor = QColor(255, 0, 0), 
                 outline_color : QColor = QColor(0, 255, 0), 
                 outline_width : float = 2) -> None:
        self.fillColor : QColor = fill_color
        self.outlineColor : QColor = outline_color
        self.outlineWidth : float = outline_width
        self.boundingBox : QRectF = bounding_box
        self.showBoundingBox : bool = False
        self.showOutline : bool = True
        self.showFillBody : bool = True
        self.__painterpath__ : QPainterPath = QPainterPath() # use of painterpath to generalize drawing function in shape

    @property
    def topLeft(self) -> QPointF:
        return self.boundingBox.topLeft()

    @property
    def topRight(self) -> QPointF:
        return self.boundingBox.topRight()
    
    @property
    def bottomLeft(self) -> QPointF:
        return self.boundingBox.bottomLeft()
    
    @property
    def bottomRight(self) -> QPointF:
        return self.boundingBox.bottomRight()

    @property
    def size(self) -> QSizeF:
        return self.boundingBox.size()
    
    @property
    def center(self) -> QPointF:
        return self.boundingBox.center()

    @topLeft.setter
    def topLeft(self, value : QPointF) -> None:
        self.boundingBox.setTopLeft(value)

    @topRight.setter
    def topRight(self, value : QPointF) -> None:
        self.boundingBox.setTopRight(value)

    @bottomLeft.setter
    def bottomLeft(self, value : QPointF) -> None:
        self.boundingBox.setBottomLeft(value)

    @bottomRight.setter
    def bottomRight(self, value : QPointF) -> None:
        self.boundingBox.setBottomRight(value)


    @size.setter
    def size(self, value : QSizeF) -> None:
        self.boundingBox.setSize(value)

    @center.setter
    def center(self, value : QPointF) -> None:
        self.boundingBox.setTopLeft(value - 0.5 * Utility.toQPointF(self.boundingBox.size()))

    def moveTopLeft(self, value : QPointF) -> None:
        self.boundingBox.moveTopLeft(value)

    def move(self, offset : QPointF) -> None:
        self.boundingBox.translate(offset)

    def draw(self, painter : QPainter) -> None:
        if (self.showFillBody):
            painter.fillPath(self.__painterpath__, QBrush(self.fillColor))
        if (self.outlineWidth > 0 and self.showOutline):
            painter.setPen(QPen(self.outlineColor, self.outlineWidth))
            painter.drawPath(self.__painterpath__)
        if (self.showBoundingBox):
            painter.setPen(QPen(Shape.boundingBoxColor, Shape.boundingBoxWidth))
            painter.drawRect(QRectF(self.boundingBox.topLeft(), 
                                    self.boundingBox.size()))
#
# rectangle shape
#
# defined by position and size (basically just a filled boundingBox)
#
class Rectangle(Shape):
    def __init__(self, position : QPointF, size : QSizeF) -> None:
        super().__init__(QRectF(position.x(), position.y(), size.width(), size.height()))

    def draw(self, painter : QPainter) -> None:
        self.__painterpath__.clear()
        self.__painterpath__.addRect(QRectF(self.boundingBox.topLeft(), 
                                            self.boundingBox.size()))
        super().draw(painter)
#
# ellipse shape
#
# defined by center-point and two radii
#
class Ellipse(Shape):
    def __init__(self, center : QPointF, radii : QSizeF) -> None:
        super().__init__(QRectF(center.x() - radii.width(), 
                                center.y() - radii.height(),
                                2 * radii.width(),
                                2 * radii.height()))
    #
    # ellipse-specific getters/setters
    #
    
    @property 
    def radii(self) -> QSizeF:
        return 0.5 * super().size
    
    @radii.setter
    def radii(self, value : QSizeF) -> None:
        super().size = value

    def draw(self, painter : QPainter) -> None:
        self.__painterpath__.clear()
        self.__painterpath__.addEllipse(self.center, self.radii.width(), self.radii.height())
        super().draw(painter)
#
# circle shape
#
# specialization of ellipse class where x and y radius are the same
#
class Circle(Ellipse):
    def __init__(self, midpoint : QPointF, radius : float):
        super().__init__(midpoint, QSizeF(radius, radius))

    #
    # circle-specific getters/setters
    #

    @property
    def radius(self) -> float:
        return 0.5 * self.radii.width()
    
    @radius.setter
    def radius(self, value : float) -> None:
        super().size = QSizeF(value, value)

    @Shape.size.setter
    def size(self, value : QSizeF) -> None:
        abs_max : float = max(abs(value.width()), abs(value.height())) # constraint that a circle must have a square boundingBox
        self.boundingBox.setSize(QSizeF(abs_max, abs_max))

#
# star shape
#
# defined by a center-point, an outer and inner size and the number of outer-vertices
#
class Star(Shape):
    def __init__(self, midpoint : QPointF, 
                 outer_size : QSizeF,
                 inner_size : QSizeF, 
                 num_outer_vertices : int = 5) -> None:
        if (num_outer_vertices < 3):
            raise AttributeError("star must have at least 3 outer vertices")
        super().__init__(QRectF(midpoint.x() - outer_size.width(), midpoint.y() - outer_size.height(), 
                                2 * outer_size.width(), 2 * outer_size.height()))
        self.__inner_size__ : QSizeF = inner_size
        self.__num_outer_vertices__ = num_outer_vertices
        self.__polygon__ : QPolygonF = QPolygonF()
        self.__compute_vertices__()

    #
    # private method to compute every vertex of the final star-polygon
    #

    def __compute_vertices__(self) -> None:
        points : list[QPointF] = []

        angle : int = 0
        inner_angle_offset : int = int(180/self.__num_outer_vertices__)
        while (angle < 360):
            points.append(self.center + 0.5 * QPointF(self.size.width() * cos(radians(angle)), 
                                                      self.size.height() * sin(radians(angle))))
            points.append(self.center + 0.5 * QPointF(self.innerSize.width() * cos(radians(angle + inner_angle_offset)), 
                                                      self.innerSize.height() * sin(radians(angle + inner_angle_offset))))
            angle += int(360/self.__num_outer_vertices__)

        self.__polygon__.clear()
        for point in points:
            self.__polygon__.append(point)

    #
    # star-specific getters/setters
    #

    @property
    def innerSize(self) -> QSizeF:
        return self.__inner_size__

    @property
    def numOuterVertices(self) -> int:
        return self.__num_outer_vertices__
    
    @Shape.topLeft.setter
    def topLeft(self, value : QPointF) -> None:
        self.boundingBox.setTopLeft(value)
        self.__compute_vertices__()

    @Shape.topRight.setter
    def topRight(self, value : QPointF) -> None:
        self.boundingBox.setTopRight(value)
        self.__compute_vertices__()

    @Shape.bottomLeft.setter
    def bottomLeft(self, value : QPointF) -> None:
        self.boundingBox.setBottomLeft(value)
        self.__compute_vertices__()

    @Shape.bottomRight.setter
    def bottomRight(self, value : QPointF) -> None:
        self.boundingBox.setBottomRight(value)
        self.__compute_vertices__()

    @Shape.size.setter
    def size(self, value : QSizeF) -> None:
        self.boundingBox.setSize(value)
        self.__compute_vertices__()

    @Shape.center.setter
    def center(self, value : QPointF) -> None:
        self.boundingBox.setTopLeft(value - 0.5 * Utility.toQPointF(self.boundingBox.size()))
        self.__compute_vertices__()

    @innerSize.setter
    def innerSize(self, value : QSizeF) -> None:
        self.__inner_size__ = value
        self.__compute_vertices__()

    @numOuterVertices.setter
    def numOuterVertices(self, value : int) -> None:
        self.__num_outer_vertices__ = value
        self.__compute_vertices__()

    def moveTopLeft(self, value : QPointF) -> None:
        self.boundingBox.moveTopLeft(value)
        self.__compute_vertices__()

    def move(self, offset : QPointF) -> None:
        self.boundingBox.translate(offset)
        self.__compute_vertices__()

    def draw(self, painter : QPainter) -> None:
        self.__painterpath__.clear()
        self.__painterpath__.addPolygon(self.__polygon__)
        super().draw(painter)