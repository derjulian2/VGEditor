#
# imports for basic vectormath utility
# and qt compatibility
#
from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QPolygonF, QTransform

from PySide6.QtCore import Qt

from math import sin, cos, radians, pi
from copy import copy, deepcopy

import enum

import Utility
#
# triangle primitive class
#
# not a shape as the others, but rather just a collection of three QPointF instances
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

    def toQPolygonF(self) -> QPolygonF:
        res : QPolygonF = QPolygonF()
        res.append(self.Vertices[0])
        res.append(self.Vertices[1])
        res.append(self.Vertices[2])
        return res
#
# base class for all other shapes
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
        
        # if advanced deformations are performed on the shape, this bool has to be set
        # to calculate/render it correctly
        self.__deformed__ : bool = False
        # use of painterpath to generalize drawing function in shape
        # NOTE: ALWAYS call QPainterPath.simplified for merging polygons into one path -> massive performance gains
        self.__painterpath__ : QPainterPath = QPainterPath()

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

    #
    # draw the shape using the passed QPainter
    # 
    # might draw in native or polygon mode, depending on what transformation were
    # executed on the shape
    #
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
    # every shape implementation should provide a way to update the underlying painterpath
    # either using:
    # - native QPainterPath.Add<Shape> method calls
    # - manual division into single polygons and add that to the PainterPath (e.g. used for advanced deformations)
    #     
    def update(self) -> None:
        raise TypeError("update() cannot be called on base shape class")
    #
    # returns underlying list of triangles to describe the shape
    #
    def describeShape(self) -> list[Triangle]:
        raise TypeError("describeShape() cannot be called on base shape class")

#
# rectangle shape
#
# defined by position and size (basically just a filled boundingBox)
#
class Rectangle(Shape):
    def __init__(self, position : QPointF, size : QSizeF) -> None:
        super().__init__(QRectF(position.x(), position.y(), size.width(), size.height()))
    
    def update(self) -> None:
        self.__painterpath__.clear()
        if (self.__deformed__):
            for triangle in self.describeShape():
                self.__painterpath__.addPolygon(triangle.toQPolygonF())
            self.__painterpath__ = self.__painterpath__.simplified()
        else:
            self.__painterpath__.addRect(self.boundingBox)

    def describeShape(self) -> list[Triangle]:
        return [ Triangle( [ self.bottomLeft, self.topLeft, self.topRight ] ), 
                 Triangle( [ self.bottomRight, self.bottomLeft, self.topRight ]) ]

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
        super().size = 2 * value
    
    def update(self) -> None:
        self.__painterpath__.clear()
        if (self.__deformed__):
            for triangle in self.describeShape():
                self.__painterpath__.addPolygon(triangle.toQPolygonF())
            self.__painterpath__ = self.__painterpath__.simplified()
        else:
            self.__painterpath__.addEllipse(self.center, self.radii.width(), self.radii.height())

    def describeShape(self) -> list[Triangle]:
        triangles : list[Triangle] = []
        width : float = 0.5 * (360 / Ellipse.Accuracy)

        points : list[QPointF] = []

        angle : float = 0.0
        while (angle < 360):
            points.append(self.center + QPointF(self.radii.width()  * sin(radians(angle - width)), 
                                                self.radii.height() * cos(radians(angle - width))))
            points.append(self.center + QPointF(self.radii.width()  * sin(radians(angle + width)), 
                                                self.radii.height() * cos(radians(angle + width))))
            angle += (360 / Ellipse.Accuracy)            

        for i in range(0, len(points), 2):
            triangles.append(Triangle([self.center, points[i], points[i+1]]))
        
        return triangles


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
        super().size = 2 * QSizeF(value, value)

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

    @numOuterVertices.setter
    def numOuterVertices(self, value : int) -> None:
        self.__num_outer_vertices__ = value

    def update(self) -> None:
        self.__painterpath__.clear()
        for triangle in self.describeShape():
            self.__painterpath__.addPolygon(triangle.toQPolygonF())
        self.__painterpath__ = self.__painterpath__.simplified()

    def describeShape(self) -> list[Triangle]:
        triangles : list[Triangle] = []
        inner_angle_offset : float = (180.0 / self.numOuterVertices)

        inner_points : list[QPointF] = []
        outer_points : list[QPointF] = []

        angle : float = 0.0

        while (angle < 360):
            # calculate inner point
            inner_points.append(self.center + QPointF(self.innerSize.width()  * sin(radians(angle + inner_angle_offset)), 
                                                      self.innerSize.height() * cos(radians(angle + inner_angle_offset))))
            # calculate outer point
            outer_points.append(self.center + QPointF(0.5 * self.size.width()  * sin(radians(angle)), 
                                                      0.5 * self.size.height() * cos(radians(angle))))
            angle += (360 / self.numOuterVertices) 

        for i in range(0, len(outer_points)):
            triangles.append(Triangle([ self.center, outer_points[i], inner_points[i]]))
            triangles.append(Triangle([ self.center, outer_points[i], inner_points[i-1]]))

        return triangles
#
# aggregate shape class
#
# defines a shape that was created via merging the vertex-data of multiple other shapes
#
class AggregateShape(Shape):
    def __init__(self, shapes : list[Shape]) -> None:

        self.__shapes__ : list[Shape] = shapes
        super().__init__(QRectF(self.__shapes__[0].topLeft, self.__shapes__[0].size))
        self.__update_boundingBox__()

    def __find_topLeft__(self) -> QPointF:
        res : QPointF = self.__shapes__[0].topLeft
        for shape in self.__shapes__:
            if (shape.topLeft.x() < res.x()):
                res.setX(shape.topLeft.x())
            if (shape.topLeft.y() < res.y()):
                res.setY(shape.topLeft.y())
        return res
    
    def __find_bottomLeft__(self) -> QPointF:
        res : QPointF = self.__shapes__[0].bottomLeft
        for shape in self.__shapes__:
            if (shape.bottomLeft_.x() < res.x()):
                res.setX(shape.bottomLeft_.x())
            if (shape.bottomLeft_.y() > res.y()):
                res.setY(shape.bottomLeft_.y())
        return res

    def __find_topRight__(self) -> QPointF:
        res : QPointF = self.__shapes__[0].topRight
        for shape in self.__shapes__:
            if (shape.topRight.x() < res.x()):
                res.setX(shape.topRight.x())
            if (shape.topRight.y() > res.y()):
                res.setY(shape.topRight.y())
        return res
    
    def __find_bottomRight__(self) -> QPointF:
        res : QPointF = self.__shapes__[0].bottomRight
        for shape in self.__shapes__:
            if (shape.bottomRight.x() > res.x()):
                res.setX(shape.bottomRight.x())
            if (shape.bottomRight.y() > res.y()):
                res.setY(shape.bottomRight.y())
        return res
    
    def __update_boundingBox__(self) -> None:
        self.boundingBox.setTopLeft(self.__find_topLeft__())
        bottomRight : QPointF = self.__find_bottomRight__()
        self.boundingBox.setSize(Utility.toQSizeF(bottomRight - self.topLeft))

    def update(self) -> None:
        self.__painterpath__.clear()
        for shape in self.__shapes__:
            shape.update()
            self.__painterpath__ = self.__painterpath__.united(shape.__painterpath__)
        self.__painterpath__ = self.__painterpath__.simplified()

    def describeShape(self) -> list[Triangle]:
        res : list[Triangle] = []
        for shape in self.__shapes__:
            res.extend(shape.describeShape())
        return res

    #
    # override setters to also apply all operations
    # to sub-shapes in respect to the shared boundingBox
    #

    @Shape.topLeft.setter
    def topLeft(self, value : QPointF) -> None:
        for shape in self.__shapes__:
            delta : QPointF = shape.topLeft - self.topLeft
            shape.topLeft = value + delta
        self.boundingBox.setTopLeft(value)

    @Shape.topRight.setter
    def topRight(self, value : QPointF) -> None:
        for shape in self.__shapes__:
            delta : QPointF = shape.topRight- self.topRight
            shape.topRight= value + delta
        self.boundingBox.setTopRight(value)

    @Shape.bottomLeft.setter
    def bottomLeft(self, value : QPointF) -> None:
        for shape in self.__shapes__:
            delta : QPointF = shape.bottomLeft - self.bottomLeft
            shape.bottomLeft = value + delta
        self.boundingBox.setBottomLeft(value)

    @Shape.bottomRight.setter
    def bottomRight(self, value : QPointF) -> None:
        for shape in self.__shapes__:
            delta : QPointF = shape.bottomRight - self.bottomRight
            shape.bottomRight = value + delta
        self.boundingBox.setBottomRight(value)

    @Shape.size.setter
    def size(self, value : QSizeF) -> None:
        # inner aspect ratio is preserved
        # a subshape covering 50% of the area before scaling
        # should still cover as much area after scaling
        # before: shape.size / self.size should equals after: shape.size / self.size
        print(value)
        for shape in self.__shapes__:
            ratio : QSizeF = Utility.QSizeFDivide(shape.size, self.size)
            shape.size = Utility.QSizeFMultiply(ratio, value)
        self.boundingBox.setSize(value)

    @Shape.center.setter
    def center(self, value : QPointF) -> None:
        for shape in self.__shapes__:
            delta : QPointF = shape.center - self.center
            shape.center = value + delta
        self.boundingBox.setTopLeft(value - 0.5 * Utility.toQPointF(self.boundingBox.size()))


    def moveTopLeft(self, value : QPointF) -> None:
        for shape in self.__shapes__:
            delta : QPointF = shape.topLeft - self.topLeft
            shape.moveTopLeft(value + delta)
        self.boundingBox.moveTopLeft(value)

    def move(self, offset : QPointF) -> None:
        self.boundingBox.translate(offset)
        for shape in self.__shapes__:
            shape.move(offset)