
from Shapes import Shape
from PySide6.QtGui import QColor, QPainter, QImage
from PySide6.QtCore import QPointF, QSizeF
from Shapes import Rectangle, Ellipse, Circle, Star, AggregateShape

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
    rectangle_1.showFillBody = False
    rectangle_1.outlineColor = QColor(0, 0, 255)
    rectangle_1.outlineWidth = 2.0

    circle_1 : Circle = Circle(QPointF(150.0, 150.0), 50.0)
    circle_1.showFillBody = False
    circle_1.outlineColor = QColor(255, 0, 0)
    circle_1.outlineWidth = 2.0

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
        rect.fillColor = QColor(0, 0, 255)
        rect.outlineColor = QColor(255, 0, 0)
        rect.outlineWidth = 2.0

    for circ in circles:
        circ.fillColor = QColor(255, 0, 0)
        circ.outlineColor = QColor(0, 0, 255)
        circ.outlineWidth = 2.0

    scene.attach_objects(rectangles)
    scene.attach_objects(circles)


def exampleScene3(scene : Scene) -> None:
    scene.clear()

    star_1 : Star = Star(QPointF(150.0, 150.0), QSizeF(150.0, 150.0), 0.5 * QSizeF(150.0, 150.0), 5)
    star_2 : Star = Star(QPointF(200.0, 200.0), QSizeF(150.0, 150.0), 0.5 * QSizeF(100.0, 100.0), 12)

    circle_1 : Circle = Circle(QPointF(-50.0,50.0), 25.0)
    ellipse_1 : Ellipse = Ellipse(QPointF(-50.0, 75.0), QSizeF(50.0, 25.0))

    scene.attach_objects([ AggregateShape([star_1, star_2]), AggregateShape([ circle_1, ellipse_1 ]) ])