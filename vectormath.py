
from PySide6.QtCore import QRect, QPoint, QSize
from PySide6.QtGui import QVector2D, QPainter, QImage, QColor, QPaintEvent, QBrush
from PySide6.QtWidgets import QWidget

def toQSize(vec : QVector2D) -> QSize:
    return QSize(int(vec.x()), int(vec.y()))

def toQPoint(vec : QVector2D) -> QPoint:
    return QPoint(int(vec.x(), int(vec.y())))

# defines how portions of a scene should be displayed

class View:
    def __init__(self, boundaries : QVector2D, upper_left : QVector2D = QVector2D(0, 0)):
        self.boundaries = boundaries
        self.upper_left = upper_left


# base class for all shapes
# provides one single interface later used in the 'Scene' class for all kinds of shapes

class Shape:
    def __init__(self, fill_color : QColor = QColor(255, 0, 0), border_color : QColor = QColor(0, 255, 0), border_width : float = 2):
        self.fill_color : QColor = fill_color
        self.border_color : QColor = border_color
        self.border_width : float = border_width

    def draw(self, painter : QPainter, view : View):
        pass

class Rectangle(Shape):
    def __init__(self, position : QVector2D, size : QVector2D):
        super().__init__()
        self.pos = position
        self.dim = size

    def draw(self, painter : QPainter, view : View):
        # draw fill rect

        painter.fillRect(QRect(QPoint(self.pos.x(), self.pos.y()), QSize(self.dim.x(), self.dim.y())), self.fill_color)
        
        #painter.fillRect(QRect(toQPoint(self.pos + 2 * QVector2D(self.border_width, self.border_width) - view.upper_left), 
        #                       toQSize(self.dim - 2 * QVector2D(self.border_width, self.border_width))),
        #                 QBrush(self.fill_color))
        # draw border
        #painter.drawRect(QRect(toQPoint(self.pos - view.upper_left), 
        #                    toQSize(self.dim)),
        #                 QBrush(self.border_color))
        

class Triangle(Shape):
    def __init__(self, vertices : list[QVector2D] ):
        super().__init__()
        if (len(vertices) != 3):
            raise AttributeError(vertices, "triangle must have 3 vertices")
        self.vertices : list[QVector2D] = vertices

    def draw(self, painter : QPainter, view : View):
        print("Triangle")

class Circle(Shape):
    def __init__(self, midpoint : QVector2D, radius : float):
        super().__init__()
        self.midpoint = midpoint
        self.radius = radius

    def draw(self, painter : QPainter, view : View):
        print("circle")

# every vector-graphics shape should be derived from
# 'Shape' class to be used in the following 'Scene' class

# using class-polymorphism, every class calls their own
# functions while being declared of type 'Shape' even though they
# could be any single specialization of 'Shape'

class Scene:
    def __init__(self):
        self.attached_elements : list[Shape] = []

    def attach_object(self, object : Shape):
        self.attached_elements.append(object)
    
    # append list of elements
    def attach_objects(self, objects : list[Shape]):
        self.attached_elements.append(objects)

    # render the entire scene using the passed painter and view
    def draw(self, painter : QPainter, view : View):
        for shape in self.attached_elements:
            shape.draw(painter, view)


class Canvas(QWidget):
    def __init__(self, parent : QWidget, dimensions : QVector2D):
        super().__init__(parent)
        self.setMinimumSize(toQSize(dimensions))

        self.image : QImage = QImage(toQSize(dimensions), QImage.Format_RGB32)
        self.painter : QPainter = QPainter()

    def paintEvent(self, event : QPaintEvent):
        painter : QPainter = QPainter(self)
        painter.drawImage(0, 0, self.image)

    def save_image(self, filepath : str):
        self.image.save(filepath)

    def load_image(self, filepath : str):
        self.image.load(filepath)
        self.update()

    def draw_scene(self, scene : Scene, view : View):
        self.painter.begin(self.image)
        scene.draw(self.painter, view)
        self.painter.end()

    def clear(self, color : QColor = QColor(255, 255, 255)):
        self.image.fill(color)
        self.update()