
from PySide6.QtCore import QRectF, QSizeF, QPointF

from PySide6.QtGui import QPainter, QColor, QPainterPath, QPen, QBrush, QPolygonF, QTransform

from PySide6.QtCore import Qt

import xml.etree.ElementTree as XMLTree

import Utility
#
# base class for all other shapes
#
# every other shape should at least
# implement all functionality of 'Shape'
#
class Shape:

    boundingBoxColor : QColor = QColor(16, 227, 206, 150)
    boundingBoxWidth : float = 2.0

    def __init__(self, boundingBox : QRectF) -> None:
        self.__painterpath__ : QPainterPath = QPainterPath()
        self.__fill_color__ : QColor = QColor()
        self.__outline_color__ : QColor = QColor()
        self.__outline_width__ : float = 0.0
        self.__show_fill_body__ : bool = True
        self.__show_bounding_box__ : bool = False
        self.__bounding_box__ : QRectF = boundingBox

    def draw(self, painter : QPainter) -> None:
        if (self.__show_fill_body__):
            painter.fillPath(self.__painterpath__, QBrush(self.__fill_color__))
        if (self.__outline_width__ > 0):
            painter.setPen(QPen(self.__outline_color__, self.__outline_width__))
            painter.drawPath(self.__painterpath__)
        if (self.__show_bounding_box__):
            painter.setPen(QPen(Shape.boundingBoxColor, Shape.boundingBoxWidth))
            painter.drawRect(QRectF(self.boundingBox.topLeft(), 
                                    self.boundingBox.size()))
    
    #
    # update() method should recalculate the shape-data to fit the bounding-box
    # and also update the painterpath for rendering
    #
    def update(self) -> None:
        raise TypeError("cannot call update() on base class") 

    #
    # describeshape() method should return raw polygon-vertex-data to describe/approximate the shape
    #
    def describeShape(self) -> QPolygonF:
        raise TypeError("cannot call describeShape() on base class")
    #
    # every shape implementation should be able to identify itself in an svg-compliant format
    #
    def toSVG(self) -> XMLTree.Element:
        raise TypeError("cannot call toSVG() on base class")

    def __make_SVG_style__(self) -> str:
        attributes : list[str] = []
        if self.__show_fill_body__:
            attributes.append(f"fill:rgb({self.__fill_color__.red()},{self.__fill_color__.green()},{self.__fill_color__.blue()})")
        if (self.__outline_width__ > 0.0):
            attributes.append(f"stroke-width:{self.__outline_width__}")
            attributes.append(f"stroke:rgb({self.__outline_color__.red()},{self.__outline_color__.green()},{self.__outline_color__.blue()})")
        return ';'.join(attributes)

    #
    # mutable properties that every shape should take into account when implementing update()
    # e.g. setting the bounding-box vertices should scale the underlying shape accordingly
    #

    @property
    def boundingBox(self) -> QRectF:
        return self.__bounding_box__
    
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
    def center(self) -> QPointF:
        return self.boundingBox.center()
    
    @property
    def size(self) -> QSizeF:
        return self.boundingBox.size()
    

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
        self.boundingBox.setTopLeft(value - 0.5 * Utility.toQPointF(self.size))
    
    #
    # translate-methods
    #

    def moveTo(self, value : QPointF) -> None:
        self.boundingBox.moveTo(value)
        
    def translate(self, offset : QPointF) -> None:
        self.boundingBox.translate(offset)

    #
    # sometimes after transformations, it could be that the topleft point is now visually not
    # in the top-left-corner of the bounding-box square
    #
    # in that case, the underlying shape can be mirrored
    # this method aims to determine that and return factors to scale your shape with accordingly
    # ( 1,  1) -> everything is as it should
    # (-1,  1) -> horizontal mirror
    # ( 1, -1) -> vertical mirror
    # (-1, -1) -> vertical and horizontal mirror
    #
    def __mirror_state__(self) -> QPointF:
        res : QPointF = QPointF(1.0 ,1.0)
        if (self.topLeft.x() > self.topRight.x()):
            res.setX(-1.0)
        if (self.topLeft.y() > self.bottomLeft.y()):
            res.setY(-1.0)
        return res
    #
    # similiar to __mirror_state__ this method returns what corner is currently visually in the topleft
    #
    def __true_topleft__(self) -> QPointF:
        m_state : QPointF = self.__mirror_state__()
        if (m_state.x() > 0 and m_state.y() > 0):
            return self.topLeft
        elif (m_state.x() > 0 and m_state.y() < 0):
            return self.bottomLeft
        elif (m_state.x() < 0 and m_state.y() > 0):
            return self.topRight
        elif (m_state.x() < 0 and m_state.y() < 0):
            return self.bottomRight
    #
    # equality operator to compare with address-values (needed for exactly comparing if a shape is another in a scene)
    # also other comparison isn't really sensible e.g. compare bounding-boxes? or color-values?
    # python also probably default-defines this
    #
    # def __eq__(self, other) -> bool:
    #     return self is other
        
#
# utility function to determine the smallest bounding-box to encompass a given set of shapes
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