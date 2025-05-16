from Shapes import Shape
from View import View

from PySide6.QtWidgets import QWidget

from PySide6.QtGui import (
    QVector2D,  QPainter,       QImage, 
    QColor,     QPaintEvent,    QMouseEvent
)

from PySide6.QtCore import QPointF, QSize, QPoint
import Utility
#
# scene class 
#
# using class-polymorphism, every shape calls their own
# functions while being declared of type 'Shape' even though they
# could be any single specialization of 'Shape'
#
# this allows for every shape to be handled behind one 
# single interface, simplifying the code for 'Scene'
#
class Scene:
    def __init__(self):
        self.attached_elements : list[Shape] = []

    def attach_object(self, object : Shape):
        self.attached_elements.append(object)
    
    # append list of elements
    def attach_objects(self, objects : list[Shape]):
        for obj in objects:
            self.attached_elements.append(obj)

    # render the entire scene using the passed painter and view
    def draw(self, painter : QPainter, view : View):
        for shape in self.attached_elements:
            shape.draw(painter, view)

    def clear(self):
        self.attached_elements.clear()
#
# canvas widget class
#
# custom qt-widget for drawing vector-graphic-shapes
# to an RGB32 image and rendering it to a window
#
class Canvas(QWidget):
    def __init__(self, parent : QWidget, dimensions : QSize):
        super().__init__(parent)
        self.setMinimumSize(dimensions)

        self.image : QImage = QImage(dimensions, QImage.Format_RGB32)
        self.scene : Scene = Scene()
        self.view : View = View(QVector2D(dimensions.width(), dimensions.height()))

        self.move_state : bool = False
        self.moving : bool = False
        self.anchor_point: QPoint = QPoint(0, 0)
        self.anchor_view_point : QPoint = QPoint(0, 0)

        self.clear()

    def setMoveMode(self, state : bool) -> None:
        self.move_state = state

    def paintEvent(self, event : QPaintEvent):
        painter : QPainter = QPainter(self)
        scene_painter : QPainter = QPainter(self.image)
        scene_painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        self.scene.draw(scene_painter, self.view)
        painter.drawImage(0, 0, self.image)

        scene_painter.end()
        painter.end()

    def mousePressEvent(self, event : QMouseEvent):
        if (self.move_state):
            self.moving = True
            self.anchor_view_point = Utility.toQPoint(self.view.top_left)
            self.anchor_point = event.pos()

    def mouseReleaseEvent(self, event : QMouseEvent):
        if (self.move_state):
            self.moving = False

    def mouseMoveEvent(self, event : QMouseEvent):
        if (self.move_state and self.moving):
            self.view.top_left = Utility.toQVector2D(self.anchor_view_point) + Utility.toQVector2D(self.anchor_point - event.pos())
            self.image.fill(QColor(255, 255, 255))
            self.update()

    def clear(self, color : QColor = QColor(255, 255, 255)):
        self.scene.clear()
        self.image.fill(color)
        self.update()