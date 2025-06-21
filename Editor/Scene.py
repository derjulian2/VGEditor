

from PySide6.QtGui import QColor, QPainter, QImage, QPolygonF
from PySide6.QtCore import QPointF, QSizeF, QSize, QRect
from Editor.Shapes.Shape import Shape
from Editor.Shapes.Primitives import Rectangle, Ellipse, Circle, Star, Polygon, Triangle
from Editor.Shapes.Aggregate import AggregateShape
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

#
# example scene 2, but all shapes are converted to polygons, subdivided and deformed
#
def exampleScene3(scene : Scene) -> None:
    scene.clear()
    example_scene_2 : Scene = Scene()
    exampleScene2(example_scene_2)
    
    for shape in example_scene_2.attachedShapes:
        shape.update()

        polygon : QPolygonF = shape.describeShape()
        polygon_subdivided : QPolygonF = MultiSubdividePolygon(polygon, 2)
        polygon_deformed : QPolygonF = DeformPolygon(polygon_subdivided, 20.0, 0.2, 0.0)
        polygon_shape : Polygon = Polygon(polygon_deformed.toList())

        polygon_shape.__fill_color__ = shape.__fill_color__
        polygon_shape.__outline_color__ = shape.__outline_color__
        polygon_shape.__outline_width__ = shape.__outline_width__

        scene.attach_object(polygon_shape)