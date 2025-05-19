import PySide6.Qt.resources
from Shapes import Shape
from View import View
import Utility

from PySide6.QtWidgets import QWidget


from PySide6.QtGui import (
    QVector2D,  QPainter,       QImage, 
    QColor,     QPaintEvent,    QMouseEvent,
    QCursor,    QWheelEvent
)

from PySide6.QtCore import QPointF, QSize, QPoint, QSizeF
from PySide6.QtCore import Qt

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
class EditorScene:
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
# editor-camera class
#
# used to modularize the behaviour of
# viewing the canvas through a viewport
#
class EditorCamera(View):
    def __init__(self, viewportSize : QSizeF):
        super().__init__(viewportSize, viewportSize)
        self.shouldMove : bool = False
        self.isMoving : bool = False

        self.anchorPoint : QPointF = QPointF()
        self.anchorViewPoint : QPointF = QPointF()

    def mousePressEvent(self, event : QMouseEvent):
        if (self.shouldMove):
            self.isMoving = True
            self.anchorPoint = Utility.QPointFCast(event.pos())

    def mouseReleaseEvent(self, event : QMouseEvent):
        if (self.shouldMove):
            self.isMoving = False

    def mouseMoveEvent(self, event : QMouseEvent):
        if (self.shouldMove and self.isMoving):
            self.center = self.anchorViewPoint + self.transformPointInverse(self.anchorPoint) - self.transformPointInverse(Utility.QPointFCast(event.pos()))
    
    def wheelEvent(self, event : QWheelEvent):
        if (self.shouldMove):
            if (event.angleDelta().y() > 0):
                self.zoomFactor = Utility.Clamp(self.zoomFactor + 0.05, 0.5, 1.75)
            else:
                self.zoomFactor = Utility.Clamp(self.zoomFactor - 0.05, 0.5, 1.75)
            self.zoom(self.zoomFactor)

#
# editor-mouse-shape class
#
# used to modularize the behaviour of editing a shape
# via mouse movements directly in the editor
#
class EditorMouseShape:
    def __init__(self):
        self.shape : Shape = None
        self.hasShape : bool = False
        self.editShape : bool = False

    def setShape(self, widget : QWidget, shape : Shape):
        self.shape = shape
        if not (self.shape is None):
            self.hasShape = True
            if not (widget is None):
                widget.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.hasShape = False
            self.editShape = False

    def cancel(self):
        self.shape = None
        self.hasShape = False

    def draw(self, painter : QPainter, view : View):
        if (self.hasShape):
            self.shape.draw(painter, view)

    def mousePressEvent(self, event : QMouseEvent, camera : EditorCamera):
        if (self.hasShape):
            self.shape.move(camera.transformPointInverse(Utility.QPointFCast(event.pos())))
            self.editShape = True

    def mouseReleaseEvent(self, widget : QWidget, event : QMouseEvent, scene : EditorScene):
        if (self.editShape):
            scene.attach_object(self.shape)
            self.setShape(None, None)
            widget.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseMoveEvent(self, event : QMouseEvent, camera : EditorCamera):
        if (self.editShape):
            self.shape.resize(camera.transformSizeInverse(Utility.QSizeFCast(Utility.QPointFCast(event.pos()) - camera.transformPoint(self.shape.boundingBox.topLeft()))))
#
# canvas widget class
#
# custom qt-widget for drawing vector-graphic-shapes
# to an RGB32 image and rendering it to a window
#
class EditorCanvas(QWidget):
    def __init__(self, parent : QWidget, dimensions : QSize):
        super().__init__(parent)
        self.setMinimumSize(dimensions)

        self.image : QImage = QImage(dimensions, QImage.Format_RGB32)

        self.scene : EditorScene = EditorScene()
        self.ems : EditorMouseShape = EditorMouseShape()
        self.camera : EditorCamera = EditorCamera(dimensions) 

        self.clear()

    #
    # decide if the canvas-camera should be
    # scrollable/moveable or not
    #
    # cancels any new-shape on mouse actions
    #
    def setMoveMode(self, state : bool) -> None:
        self.camera.shouldMove = state
        self.ems.cancel()

    #
    # method to attach a temporary shape to the mouse cursor
    # this shape will always be displayed at the coordinates of the mouse cursor
    # projected to the corresponding world-coordinates
    #
    # cancels any camera-move actions
    #
    def attachToMouse(self, shape : Shape):
        self.camera.shouldMove = False
        self.ems.setShape(self, shape)
        

    def paintEvent(self, event : QPaintEvent):
        painter : QPainter = QPainter(self)
        scene_painter : QPainter = QPainter(self.image)
        scene_painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        self.scene.draw(scene_painter, self.camera)
        self.ems.draw(scene_painter, self.camera)
        painter.drawImage(0, 0, self.image)

        scene_painter.end()
        painter.end()

    def mousePressEvent(self, event : QMouseEvent):
        self.camera.mousePressEvent(event)
        self.ems.mousePressEvent(event, self.camera)

    def mouseReleaseEvent(self, event : QMouseEvent):
        self.camera.mouseReleaseEvent(event)
        self.ems.mouseReleaseEvent(self, event, self.scene)

    def mouseMoveEvent(self, event : QMouseEvent):
        self.camera.mouseMoveEvent(event)
        self.ems.mouseMoveEvent(event, self.camera)

        self.image.fill(QColor(255, 255, 255))
        self.update()

    def wheelEvent(self, event : QWheelEvent):
        self.camera.wheelEvent(event)
        
        self.image.fill(QColor(255, 255, 255))
        self.update()

    def clear(self, color : QColor = QColor(255, 255, 255)):
        self.scene.clear()
        self.camera.center = QPointF(0.0, 0.0)
        self.camera.zoomFactor = 1.0
        self.image.fill(color)
        self.update()