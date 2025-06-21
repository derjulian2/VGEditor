from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QPolygonF, QTransform

from PySide6.QtCore import Qt

from math import sin, cos, radians, pi

import xml.etree.ElementTree as XMLTree

import Utility
from Editor.Shapes.Shape import Shape
#
# polygon primitive
#
# this primitive is special in that advanced deformations can only be performed on it as
# it is the only one that can be represented through raw-vertex-data
#
# all other primitives have to be converted to this shape before such deformations can
# be performed on it (see describeShape())
#
class Polygon(Shape):

    def __init__(self, vertices : list[QPointF]) -> None:
        self.__polygon__ : QPolygonF = QPolygonF(vertices)
        super().__init__(self.__polygon__.boundingRect())

    def update(self) -> None:
        # fit polygon into bounding-box
        self.__fit_polygon_to_bounding_box__()
        # update painterpath
        self.__painterpath__.clear()
        self.__painterpath__.addPolygon(self.__polygon__)
        self.__painterpath__ = self.__painterpath__.simplified()

    def describeShape(self) -> QPolygonF:
        return self.__polygon__

    def toSVG(self) -> XMLTree.Element:
        points : str = ""
        for point in self.__polygon__.toList():
            points += f"{point.x()},{point.y()} "
        return XMLTree.Element("polygon", {"points" : points,
                                           "style" : self.__make_SVG_style__()})
    #
    # method to fit the polygon-data into the bounding-box
    #
    # scale polygon down to sidelengths of x = 1 and y = 1
    # then every vertex can be interpreted as a ratio in the bounding-box
    # a be safely scaled up to the new size
    # after that, just translate correctly
    #
    # this can be simplified to directly scaling from old-size to new-size
    #
    def __fit_polygon_to_bounding_box__(self) -> None:

        old_pos : QPointF = self.__polygon__.boundingRect().topLeft()
        old_size : QSizeF = self.__polygon__.boundingRect().size()
        old_center : QPointF  = self.__polygon__.boundingRect().center()

        # set size artificially here, or else division by zero occurs
        # effect should be barely noticeable
        if (old_size.width() == 0):
            old_size.setWidth(0.01)
        if (old_size.height() == 0):
            old_size.setHeight(0.01)

        delta_pos  : QPointF = self.__true_topleft__() - old_pos
        delta_scale : QSizeF = Utility.QSizeFDivide(Utility.QSizeFAbs(self.size), old_size)

        if (delta_scale.width() == 0 or delta_scale.height() == 0):
            return # return here, because scaling would lose all data by multiplying with 0

        # now apply all transformations
        scale_transform : QTransform = QTransform.fromScale(delta_scale.width(), delta_scale.height())
        # for scaling to apply correctly polygon's center is moved to origin, then scaled, then translated back
        self.__polygon__.translate(-old_center)
        self.__polygon__ = scale_transform.map(self.__polygon__)
        self.__polygon__.translate(old_center + delta_pos)
    
#
# triangle primitive that consists of a single 3-sided polygon
#
# essentially just a polygon with constraints
#
class Triangle(Polygon):
    
    def __init__(self, vertices : list[QPointF]) -> None:
        if (len(vertices) != 3):
            raise AttributeError("triangle requires 3 vertices as input")
        super().__init__(vertices)
#
# rectangle primitive
#
class Rectangle(Shape):

    def __init__(self, topleft : QPointF, size : QSizeF):
        super().__init__(QRectF(topleft, size))

    def update(self) -> None:
        # fit polygon into bounding-box
            # nothing to do, as bounding-box is already the entire shape
        # update painterpath
        self.__painterpath__.clear()
        self.__painterpath__.addRect(self.__bounding_box__)

    def describeShape(self) -> QPolygonF:
        return self.__painterpath__.toFillPolygon()
    
    def toSVG(self) -> XMLTree.Element:
        return XMLTree.Element("rect", { "x" : str(self.topLeft.x()),
                                         "y" : str(self.topLeft.y()),
                                         "width" : str(self.size.width()),
                                         "height" : str(self.size.height()),
                                         "style" : self.__make_SVG_style__()})

#
# ellipse primitive
#
class Ellipse(Shape):

    def __init__(self, center : QPointF, radii : QSizeF):
        super().__init__(QRectF(center.x() - radii.width(), 
                                center.y() - radii.height(),
                                2 * radii.width(),
                                2 * radii.height()))
        
    def update(self) -> None:
        # fit polygon into bounding-box
            # nothing to do, as bounding-box and radii already describe the entire shape, let QT handle everything else
        # update painterpath
        self.__painterpath__.clear()
        self.__painterpath__.addEllipse(self.center, self.radii.width(), self.radii.height())

    def describeShape(self) -> QPolygonF:
        return self.__painterpath__.toFillPolygon()
    
    def toSVG(self) -> XMLTree.Element:
        return XMLTree.Element("ellipse", {"cx" : str(self.center.x()), 
                                           "cy" : str(self.center.y()),
                                           "rx" : str(self.radii.width()),
                                           "ry" : str(self.radii.height()),
                                           "style" : self.__make_SVG_style__()})
    
    @property 
    def radii(self) -> QSizeF:
        return 0.5 * self.size
    
    @radii.setter
    def radii(self, value : QSizeF) -> None:
        self.size = 2 * value

#
# circle primitive
#
class Circle(Ellipse):

    def __init__(self, center : QPointF, radius : float):
        super().__init__(center, QSizeF(radius, radius))
    
    def toSVG(self) -> XMLTree.Element:
        return XMLTree.Element("circle", {"cx" : str(self.center.x()), 
                                          "cy" : str(self.center.y()),
                                          "r" : str(self.radius),
                                          "style" : self.__make_SVG_style__()})

    @property
    def radius(self) -> float:
        return self.radii.width()

    @radius.setter
    def radius(self, value : float) -> None:
        super().size = 2 * QSizeF(value, value)


    @Shape.size.setter
    def size(self, value : QSizeF) -> None:
        abs_min : float = min(abs(value.width()), abs(value.height())) # constraint that a circle must have a square boundingBox
        self.boundingBox.setSize(QSizeF(abs_min, abs_min))

#
# star primitive
#
# also essentially just a polygon with constraints
#
class Star(Polygon):

    def __init__(self, center : QPointF, outer_size : QSizeF, inner_size : QSizeF, spike_num : int) -> None:
        self.__spike_num__ : int = spike_num
        self.__inner_size__ : QSizeF = inner_size
        super().__init__(self.__compute_vertices__(center, outer_size, inner_size, spike_num))

    def describeShape(self) -> QPolygonF:
        return self.__polygon__
    
    @property
    def SpikeNum(self) -> int:
        return self.__spike_num__
    
    @property
    def InnerSize(self) -> QSizeF:
        return self.__inner_size__

    @SpikeNum.setter
    def SpikeNum(self, value : int) -> None:
        self.__spike_num__ = value

    @InnerSize.setter
    def InnerSize(self, value : QSizeF) -> None:
        self.__inner_size__ = value

    def __compute_vertices__(self, center : QPointF, outer_size : QSizeF, inner_size : QSizeF, spike_num : int) -> list[QPointF]:
        res : list[QPointF] = []

        inner_angle_offset : float = (180.0 / spike_num)
        angle : float = 0.0

        while (angle < 360):
            # calculate outer point
            res.append(center + QPointF(outer_size.width()  * sin(radians(angle)), 
                                        outer_size.height() * cos(radians(angle))))
            # calculate inner point
            res.append(center + QPointF(inner_size.width() * sin(radians(angle + inner_angle_offset)), 
                                        inner_size.height() * cos(radians(angle + inner_angle_offset))))
            angle += (360 / spike_num) 

        return res

#
# utility functions to approximate shapes into triangles for deformations
#

#
# splits rectangle into two triangles along it's diagonal
#
def triangulateRectangle(rect : Rectangle) -> list[Triangle]:
    return [ Triangle([rect.bottomLeft, rect.topLeft, rect.topRight]), 
             Triangle([rect.bottomLeft, rect.topRight, rect.bottomRight]) ]

#
# requires polygon-triangulation -> there seems to be a qt-libary for this, but this is not necessary here at all for now
# deformations can be applied to triangles and then be batched into a polygon for rendering
#
def triangulatePolygon(poly : Polygon) -> list[Triangle]:
    pass
#
# approximates ellipse with triangles
#
def triangulateEllipse(ellipse : Ellipse, accuracy : int) -> list[Triangle]: # a circle is also an ellipse, so this function also covers circle
    triangles : list[Triangle] = []
    width : float = 0.5 * (360 / accuracy)

    points : list[QPointF] = []

    angle : float = 0.0
    while (angle < 360):
        points.append(ellipse.center + QPointF(ellipse.radii.width()  * sin(radians(angle - width)), 
                                               ellipse.radii.height() * cos(radians(angle - width))))
        points.append(ellipse.center + QPointF(ellipse.radii.width()  * sin(radians(angle + width)), 
                                               ellipse.radii.height() * cos(radians(angle + width))))
        angle += (360 / accuracy)            

    for i in range(0, len(points), 2):
        triangles.append(Triangle([ellipse.center, points[i], points[i+1]]))
    
    return triangles
#
# constructs star shape from triangles
#
def triangulateStar(star : Star) -> list[Triangle]:
    triangles : list[Triangle] = []
    inner_angle_offset : float = (180.0 / star.SpikeNum)

    inner_points : list[QPointF] = []
    outer_points : list[QPointF] = []

    angle : float = 0.0

    while (angle < 360):
        # calculate inner point
        inner_points.append(star.center + QPointF(star.InnerSize.width()  * sin(radians(angle + inner_angle_offset)), 
                                                    star.InnerSize.height() * cos(radians(angle + inner_angle_offset))))
        # calculate outer point
        outer_points.append(star.center + QPointF(0.5 * star.size.width()  * sin(radians(angle)), 
                                                    0.5 * star.size.height() * cos(radians(angle))))
        angle += (360 / star.SpikeNum) 

    for i in range(0, len(outer_points)):
        triangles.append(Triangle([ star.center, outer_points[i], inner_points[i]]))
        triangles.append(Triangle([ star.center, outer_points[i], inner_points[i-1]]))

    return triangles