

from PySide6.QtGui import QColor, QPainter, QImage, QPolygonF
from PySide6.QtCore import QPointF, QSizeF
from Editor.Shapes.Shape import Shape
from Editor.Shapes.Primitives import Rectangle, Ellipse, Circle, Star, Polygon, Triangle
from Editor.Shapes.DeformShapes import MultiSubdividePolygon, DeformPolygon

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
    def __init__(self) -> None:
        self.attachedShapes : list[Shape] = []
        self.backgroundColor : QColor = QColor(255, 255, 255)

    def attach_object(self, object : Shape) -> None:
        self.attachedShapes.append(object)
    
    # append list of elements
    def attach_objects(self, objects : list[Shape]) -> None:
        for obj in objects:
            self.attachedShapes.append(obj)

    def moveToFront(self, shape : Shape):
        for i in range(0, len(self.attachedShapes)):
            if (self.attachedShapes[i] is shape):
                self.attachedShapes.append(self.attachedShapes[i])
                self.attachedShapes.pop(i)
    #
    # updates each shape in the scene, possibly performing vertex-recalculations
    #
    def update(self) -> None:
        for shape in self.attachedShapes:
            shape.update()
    #
    # render the entire scene using the passed painter onto the passed image
    #
    def draw(self, painter : QPainter, image : QImage) -> None:
        image.fill(self.backgroundColor)
        for shape in self.attachedShapes:
            shape.draw(painter)

    def clear(self) -> None:
        self.attachedShapes.clear()

def exampleScene1(scene : Scene) -> None:
    scene.clear()

    rectangle_1 : Rectangle = Rectangle(QPointF(100.0, 100.0), QSizeF(100.0, 100.0))
    rectangle_1.__show_fill_body__ = False
    rectangle_1.__outline_color__ = QColor(0, 0, 255)
    rectangle_1.__outline_width__ = 2.0

    circle_1 : Circle = Circle(QPointF(150.0, 150.0), 50.0)
    circle_1.__show_fill_body__ = False
    circle_1.__outline_color__ = QColor(255, 0, 0)
    circle_1.__outline_width__ = 2.0

    scene.attach_objects([rectangle_1, circle_1])

def exampleScene2(scene : Scene) -> None:
    scene.clear()

    padding : float = 5.0
    rectangles : list[Rectangle] = [Rectangle(QPointF(200.0 + padding, 100.0), QSizeF(100.0, 100.0)),
                                    Rectangle(QPointF(300.0 + 2 * padding, 100.0), QSizeF(100.0, 100.0)),
                                    Rectangle(QPointF(100.0, 200.0 + padding), QSizeF(100.0, 100.0)),
                                    Rectangle(QPointF(200.0 + padding, 300.0 + 2 * padding), QSizeF(100.0, 100.0)),
                                    Rectangle(QPointF(300.0 + 2 * padding, 300.0 + 2 * padding), QSizeF(100.0, 100.0)),
                                    Rectangle(QPointF(400.0 + 3 * padding, 200.0 + padding), QSizeF(100.0, 100.0))]

    circles : list[Circle] = [Circle(QPointF(150.0, 150.0), 50.0), 
                                Circle(QPointF(450.0 + 3 * padding, 150.0), 50.0), 
                                Circle(QPointF(450.0 + 3 * padding, 350.0 + 2 * padding), 50.0), 
                                Circle(QPointF(150.0, 350.0 + 2 * padding), 50.0)]

    for rect in rectangles:
        rect.__fill_color__ = QColor(0, 0, 255)
        rect.__outline_color__ = QColor(255, 0, 0)
        rect.__outline_width__ = 2.0

    for circ in circles:
        circ.__fill_color__ = QColor(255, 0, 0)
        circ.__outline_color__ = QColor(0, 0, 255)
        circ.__outline_width__ = 2.0

    scene.attach_objects(rectangles)
    scene.attach_objects(circles)


def exampleScene3(scene : Scene) -> None:
    scene.clear()

    star_1 : Star = Star(QPointF(150.0, 150.0), QSizeF(150.0, 150.0), 0.5 * QSizeF(150.0, 150.0), 5)
    star_1.update()

    rect_1 : Rectangle = Rectangle(QPointF(50.0, 50.0), QSizeF(100.0, 100.0))
    rect_1.update()

    star_deformed : QPolygonF = DeformPolygon(MultiSubdividePolygon(star_1.describeShape(), 3), 10, 0.5, 0.0)
    rect_deformed : QPolygonF = DeformPolygon(MultiSubdividePolygon(rect_1.describeShape(), 3), 10, 0.5, 0.0)

    poly_1 : Polygon = Polygon(rect_deformed.toList())

    scene.attach_object(poly_1)

