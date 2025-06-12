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

    def Vertex(self, index : int) -> QPointF:
        if (index < 0 or index > 2):
            raise AttributeError("triangle vertex index out of range")
        return self.__vertices__[index]

    def setVertex(self, index : int, value : QPointF) -> None:
        if (index < 0 or index > 2):
            raise AttributeError("triangle vertex index out of range")
        self.__vertices__[index] = value

    def move(self, offset : QPointF) -> None:
        self.__vertices__ = [
            self.__vertices__[0] + offset,
            self.__vertices__[1] + offset,
            self.__vertices__[2] + offset
        ]

    def toQPolygonF(self) -> QPolygonF:
        res : QPolygonF = QPolygonF()
        res.append(self.Vertices[0])
        res.append(self.Vertices[1])
        res.append(self.Vertices[2])
        return res
    
from DeformShapes import Subdivide, Deformation
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
# determine the bounding box of a list of triangles (for coordinate systems with positive x and negative y)
#
def findBoundingBoxTriangles(triangles : list[Triangle]) -> QRectF:
    topLeft : QPointF = triangles[0].Vertices[0].__copy__()
    bottomRight : QPointF = triangles[0].Vertices[1].__copy__()
    for triangle in triangles:
        for vertex in triangle.Vertices:
            if vertex.x() < topLeft.x():
                topLeft.setX(vertex.x())
            if (vertex.y() < topLeft.y()):
                topLeft.setY(vertex.y())
            if (vertex.x() > bottomRight.x()):
                bottomRight.setX(vertex.x())
            if (vertex.y() > bottomRight.y()):
                bottomRight.setY(vertex.y())
    return QRectF(topLeft, Utility.toQSizeF(bottomRight - topLeft))
#
# determine bounding box of a list of shapes (for coordinate systems with positive x and negative y)
#
def findBoundingBoxShapes(shapes : list[Shape]) -> QRectF:
    topLeft : QPointF = shapes[0].topLeft.__copy__()
    bottomRight : QPointF = shapes[0].bottomRight.__copy__()
    for shape in shapes:
        if shape.topLeft.x() < topLeft.x():
            topLeft.setX(shape.topLeft.x())
        if (shape.topLeft.y() < topLeft.y()):
            topLeft.setY(shape.topLeft.y())
        if (shape.bottomRight.x() > bottomRight.x()):
            bottomRight.setX(shape.bottomRight.x())
        if (shape.bottomRight.y() > bottomRight.y()):
            bottomRight.setY(shape.bottomRight.y())
    return QRectF(topLeft, Utility.toQSizeF(bottomRight - topLeft))
#
# generalization of a shape consisting of multiple triangles
#
# later useful for making up aggregate shapes and applying deformations (although resource-intensive)
#
class Polygon(Shape):
    def __init__(self, triangles : list[Triangle]):
        self.__triangles__ : list[Triangle] = triangles
        super().__init__(findBoundingBoxTriangles(triangles))

    def describeShape(self) -> list[Triangle]:
        return self.__triangles__
    
    def update(self) -> None:
        self.__painterpath__.clear()
        for triangle in self.describeShape():
            path : QPainterPath = QPainterPath()
            path.addPolygon(triangle.toQPolygonF())
            self.__painterpath__ = self.__painterpath__.united(path)
        self.__painterpath__ = self.__painterpath__.simplified()

    #
    # specializes setters that update every point of every triangle
    #

    def __fit_polygon_to_boundingBox__(self, newBox : QRectF) -> None:
        for triangle in self.__triangles__:
            ratio_0 : QPointF = Utility.QPointFDivide(triangle.Vertex(0) - self.topLeft, Utility.toQPointF(self.size))
            ratio_1 : QPointF = Utility.QPointFDivide(triangle.Vertex(1) - self.topLeft, Utility.toQPointF(self.size))
            ratio_2 : QPointF = Utility.QPointFDivide(triangle.Vertex(2) - self.topLeft, Utility.toQPointF(self.size))
            triangle.setVertex(0, newBox.topLeft() + Utility.QPointFMultiply(ratio_0, Utility.toQPointF(newBox.size())))
            triangle.setVertex(1, newBox.topLeft() + Utility.QPointFMultiply(ratio_1, Utility.toQPointF(newBox.size())))
            triangle.setVertex(2, newBox.topLeft() + Utility.QPointFMultiply(ratio_2, Utility.toQPointF(newBox.size())))

    @Shape.topLeft.setter
    def topLeft(self, value : QPointF) -> None:
        newBox : QRectF = QRectF(self.boundingBox)
        newBox.setTopLeft(value)
        self.__fit_polygon_to_boundingBox__(newBox)
        self.boundingBox.setTopLeft(value)


    @Shape.topRight.setter
    def topRight(self, value : QPointF) -> None:
        newBox : QRectF = QRectF(self.boundingBox)
        newBox.setTopRight(value)
        self.__fit_polygon_to_boundingBox__(newBox)
        self.boundingBox.setTopRight(value)


    @Shape.bottomLeft.setter
    def bottomLeft(self, value : QPointF) -> None:
        newBox : QRectF = QRectF(self.boundingBox)
        newBox.setBottomLeft(value)
        self.__fit_polygon_to_boundingBox__(newBox)
        self.boundingBox.setBottomLeft(value)


    @Shape.bottomRight.setter
    def bottomRight(self, value : QPointF) -> None:
        newBox : QRectF = QRectF(self.boundingBox)
        newBox.setBottomRight(value)
        self.__fit_polygon_to_boundingBox__(newBox)
        self.boundingBox.setBottomRight(value)


    @Shape.size.setter
    def size(self, value : QSizeF) -> None:
        newBox : QRectF = QRectF(self.boundingBox)
        newBox.setSize(value)
        self.__fit_polygon_to_boundingBox__(newBox)
        self.boundingBox.setSize(value)
    

    @Shape.center.setter
    def center(self, value : QPointF) -> None:
        newBox : QRectF = QRectF(self.boundingBox)
        newBox.setTopLeft(value - 0.5 * Utility.toQPointF(self.boundingBox.size()))
        self.__fit_polygon_to_boundingBox__(newBox)
        self.boundingBox.setTopLeft(value - 0.5 * Utility.toQPointF(self.boundingBox.size()))

    def moveTopLeft(self, value : QPointF) -> None:
        for triangle in self.__triangles__:
            triangle.setVertex(0, value + triangle.Vertex(0) - self.topLeft)
            triangle.setVertex(1, value + triangle.Vertex(1) - self.topLeft)
            triangle.setVertex(2, value + triangle.Vertex(2) - self.topLeft)
        self.boundingBox.moveTopLeft(value)
        

    def move(self, offset : QPointF) -> None:
        for triangle in self.__triangles__:
            triangle.move(offset)
        self.boundingBox.translate(offset)

    def DeformAlongCurve(self, amplitude : float, width : float, offset : float) -> None:
        self.__deformed__ = True
        self.__triangles__ = Deformation(self.__triangles__, amplitude, width, offset)
        self.boundingBox = findBoundingBoxTriangles(self.__triangles__)


    def SubdivideTriangles(self, n : int) -> None:
        res : list[Triangle] = self.__triangles__.copy()

        for i in range(0, n):
            iteration : list[Triangle] = []
            for triangle in res:
                iteration.extend(Subdivide(triangle))
            res = iteration
        
        self.__triangles__ = res

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
    Accuracy : int = 32

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
        super().__init__(findBoundingBoxShapes(self.__shapes__))

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

    def __fit_subshapes_to_boundingBox__(self, newBox : QRectF) -> None:
        for shape in self.__shapes__:
            pass
        pass

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
            delta : QPointF = shape.topRight - self.topRight
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