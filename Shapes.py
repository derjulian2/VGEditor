#
# imports for basic vectormath utility
# and qt compatibility
#
from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QPolygonF

from PySide6.QtCore import Qt

from math import sin, cos, radians, pi

import Utility
#
# triangle primitive
#
class Triangle:
    def __init__(self, vertices : list[QPointF]) -> None:
        if (len(vertices) != 3):
            raise AttributeError("Triangle must have exactly 3 vertices")
        self.__vertices__ : list[QPointF] = vertices

    @property
    def Vertices(self) -> list[QPointF]:
        return self.__vertices__

    @Vertices.setter
    def Vertices(self, value : list[QPointF]) -> None:
        if (len(value) != 3):
            raise AttributeError("Triangle must have exactly 3 vertices")
        self.__vertices__ = value

#
# subdivides a triangle into four smaller triangles along the center points at the sides
#
def Subdivide(triangle : Triangle) -> list[Triangle]:
    # alias vertices
    a_v : QPointF = triangle.Vertices[0]
    b_v : QPointF = triangle.Vertices[1]
    c_v : QPointF = triangle.Vertices[2]
    # determine centers of triangle sides
    center_ac : QPointF = a_v + 0.5 * (c_v - a_v)
    center_bc : QPointF = b_v + 0.5 * (c_v - b_v)
    center_ab : QPointF = a_v + 0.5 * (b_v - a_v)
    # span new triangles between vertices and new points
    return [ Triangle([ a_v, center_ab, center_ac ]),
             Triangle([ b_v, center_bc, center_ab ]),
             Triangle([ c_v, center_bc, center_ac ]),
             Triangle([ center_ab, center_bc, center_ac ])]
#
# deforms a list of triangles along a sine wave with parameters a, w and o for amplitude, width and offset
#
# f(x) = a * sin(2pi * w * x + o) is essentially added to each point of every triangle in 'triangles'
#
def Deformation(triangles : list[Triangle], amplitude : float, width : float, offset : float) -> list[Triangle]:
    result : list[Triangle] = []
    for triangle in triangles:
        result.append(Triangle([ triangle.Vertices[0] + QPointF(0.0, amplitude * sin(2 * pi * width * triangle.Vertices[0] + offset)),
                                 triangle.Vertices[1] + QPointF(0.0, amplitude * sin(2 * pi * width * triangle.Vertices[1] + offset)),
                                 triangle.Vertices[2] + QPointF(0.0, amplitude * sin(2 * pi * width * triangle.Vertices[2] + offset)), ]))
    return result

#
# base class for all other shapes
#
# this class needs to be rebuilt completely to support division into triangles
#
# every other shape should at least
# implement all functionality of 'Shape'
#
class Shape:

    boundingBoxColor : QColor = QColor(16, 227, 206, 150)
    boundingBoxWidth : float = 2

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
        self.__triangles__ : list[Triangle] = []
        self.__painterpath__ : QPainterPath = QPainterPath() # use of painterpath to generalize drawing function in shape
        self.__update_vertices__()

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
        self.__update_vertices__()

    @topRight.setter
    def topRight(self, value : QPointF) -> None:
        self.boundingBox.setTopRight(value)
        self.__update_vertices__()

    @bottomLeft.setter
    def bottomLeft(self, value : QPointF) -> None:
        self.boundingBox.setBottomLeft(value)
        self.__update_vertices__()

    @bottomRight.setter
    def bottomRight(self, value : QPointF) -> None:
        self.boundingBox.setBottomRight(value)
        self.__update_vertices__()

    @size.setter
    def size(self, value : QSizeF) -> None:
        self.boundingBox.setSize(value)
        self.__update_vertices__()

    @center.setter
    def center(self, value : QPointF) -> None:
        self.boundingBox.setTopLeft(value - 0.5 * Utility.toQPointF(self.boundingBox.size()))
        self.__update_vertices__()

    def moveTopLeft(self, value : QPointF) -> None:
        self.boundingBox.moveTopLeft(value)
        self.__update_vertices__()

    def move(self, offset : QPointF) -> None:
        self.boundingBox.translate(offset)
        self.__update_vertices__()

    def draw(self, painter : QPainter) -> None:
        polygon : QPolygonF = QPolygonF()
        for triangle in self.__triangles__:
            polygon.append([ triangle.Vertices[0], triangle.Vertices[1], triangle.Vertices[2]])
        painter.drawPolygon(polygon)
        
        # if (self.showFillBody):
        #     painter.fillPath(self.__painterpath__, QBrush(self.fillColor))
        # if (self.outlineWidth > 0 and self.showOutline):
        #     painter.setPen(QPen(self.outlineColor, self.outlineWidth))
        #     painter.drawPath(self.__painterpath__)
        # if (self.showBoundingBox):
        #     painter.setPen(QPen(Shape.boundingBoxColor, Shape.boundingBoxWidth))
        #     painter.drawRect(QRectF(self.boundingBox.topLeft(), 
        #                             self.boundingBox.size()))

    def describeShape(self) -> list[Triangle]:
        return self.__triangles__
    #
    # updates the underlying painterpath according to the currently stored polygon
    #
    def __update_painterpath__(self) -> None:
        pass
        # polygon : QPolygonF = QPolygonF()
        # for triangle in self.__triangles__:
        #     polygon.append([ triangle.Vertices[0], triangle.Vertices[1], triangle.Vertices[2]])
        # self.__painterpath__.clear()
        # self.__painterpath__.addPolygon(polygon)
    #
    # updates currently stored polygon according to the bounding box
    #
    def __update_vertices__(self) -> None:
        raise TypeError("__update_vertices__() requires shape specialization but was called from base class")

#
# rectangle shape
#
# defined by position and size (basically just a filled boundingBox)
#
class Rectangle(Shape):
    def __init__(self, position : QPointF, size : QSizeF) -> None:
        super().__init__(QRectF(position.x(), position.y(), size.width(), size.height()))
    
    def __update_vertices__(self) -> None:
        self.__triangles__ = [ Triangle( [ self.bottomLeft, self.topLeft, self.topRight ] ), 
                               Triangle( [ self.bottomRight, self.bottomLeft, self.topRight ] )]
        self.__update_painterpath__()

#
# ellipse shape
#
# defined by center-point and two radii
#
class Ellipse(Shape):

    #
    # determines the number of triangles that the ellipse will be split up into
    # when rendering (Ellipse shape will  be approximated)
    #
    Accuracy : int = 16

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
    
    def __update_vertices__(self) -> None:
        self.__triangles__.clear()
        width : float = 0.5 * (360 / Ellipse.Accuracy)
        scale_factor : float = 360 / Ellipse.Accuracy # mapping factor to cover the entire circle
        for angle in range(0, Ellipse.Accuracy):
            self.__triangles__.append(Triangle([ self.center, 
                                                 self.center + QPointF(self.radii.width()  * sin(radians(scale_factor * (angle - width))), 
                                                                       self.radii.height() * cos(radians(scale_factor * (angle - width)))), 
                                                 self.center + QPointF(self.radii.width()  * sin(radians(scale_factor * (angle + width))), 
                                                                       self.radii.height() * cos(radians(scale_factor * (angle + width)))) ]))
        self.__update_painterpath__()

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
        self.__update_vertices__()

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
        self.__inner_size__ : QSizeF = inner_size
        self.__num_outer_vertices__ : int = num_outer_vertices
        super().__init__(QRectF(midpoint.x() - outer_size.width(), midpoint.y() - outer_size.height(), 
                                2 * outer_size.width(), 2 * outer_size.height()))

    #
    # star-specific getters/setters
    #

    @property
    def innerSize(self) -> QSizeF:
        return self.__inner_size__

    @property
    def numOuterVertices(self) -> int:
        return self.__num_outer_vertices__

    @innerSize.setter
    def innerSize(self, value : QSizeF) -> None:
        self.__inner_size__ = value
        self.__update_vertices__()

    @numOuterVertices.setter
    def numOuterVertices(self, value : int) -> None:
        self.__num_outer_vertices__ = value
        self.__update_vertices__()

    #
    # private method to compute every vertex of the final star-polygon
    #

    def __update_vertices__(self) -> None:
        self.__triangles__.clear()
        inner_angle_offset : float = (180.0 / self.numOuterVertices)
        scale_factor : float = 360.0 / self.numOuterVertices # mapping factor to cover the entire circle
        for angle in range(0, self.numOuterVertices):
            outer_point : QPointF = self.center + QPointF(0.5 * self.size.width() * sin(radians(scale_factor * angle)), 0.5 * self.size.height() * cos(radians(scale_factor * angle)))
            
            inner_point_a : QPointF = self.center + QPointF(0.5 * self.innerSize.width() * sin(radians(scale_factor * (angle - inner_angle_offset))), self.innerSize.height() * cos(radians(scale_factor * (angle - inner_angle_offset))))
            inner_point_b : QPointF = self.center + QPointF(0.5 * self.innerSize.width() * sin(radians(scale_factor * (angle + inner_angle_offset))), self.innerSize.height() * cos(radians(scale_factor * (angle + inner_angle_offset))))
            
            self.__triangles__.append(Triangle([ self.center, inner_point_a, outer_point ])) # some redundancy here as same point will be calculated twice
            self.__triangles__.append(Triangle([ self.center, inner_point_b, outer_point ]))

        self.__update_painterpath__()
