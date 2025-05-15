from Shapes import Shape
from View import View

from PySide6.QtWidgets import QWidget

from PySide6.QtGui import (
    QVector2D,  QPainter,       QImage, 
    QColor,     QPaintEvent
)

from PySide6.QtCore import QPointF, QSize
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

        self.clear()

    def paintEvent(self, event : QPaintEvent):
        painter : QPainter = QPainter(self)
        scene_painter : QPainter = QPainter(self.image)

        self.scene.draw(scene_painter, self.view)
        painter.drawImage(0, 0, self.image)

        scene_painter.end()
        painter.end()


    def save_image(self, filepath : str):
        self.image.save(filepath)

    def load_image(self, filepath : str):
        self.image.load(filepath)
        self.update()

    def clear(self, color : QColor = QColor(255, 255, 255)):
        self.image.fill(color)
        self.update()