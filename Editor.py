
from Shapes import Shape
from View import View
import Utility

from enum import Enum

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
    def __init__(self) -> None:
        self.attachedShapes : list[Shape] = []
        self.backgroundColor : QColor = QColor(255, 255, 255)

    def attach_object(self, object : Shape) -> None:
        self.attachedShapes.append(object)
    
    # append list of elements
    def attach_objects(self, objects : list[Shape]) -> None:
        for obj in objects:
            self.attachedShapes.append(obj)

    # render the entire scene using the passed painter and view
    def draw(self, painter : QPainter, image : QImage) -> None:
        image.fill(self.backgroundColor)
        for shape in self.attachedShapes:
            shape.draw(painter)

    def clear(self) -> None:
        self.attachedShapes.clear()
#
# editorstate enum
#
# describes the user-interaction-state that the editor is in
#
class EditorState(Enum):
    NONE = 0                # when the user is not doing anything except viewing the scene
    ADD_NEW_SHAPE = 1       # when the user is adding a new shape via the editor-window
    EDIT_EXISTING_SHAPE = 2 # when the user is editing the properties of an already existing shape
    SCROLL_VIEWPORT = 3     # when the user is scrolling the camera around the scene
#
# editor-camera class
#
# stores information about viewing the canvas through a view
#
class EditorCamera(View):
    def __init__(self, viewportSize : QSizeF) -> None:
        super().__init__(viewportSize, viewportSize)
        self.anchorPoint : QPointF = QPointF()
        self.anchorViewPoint : QPointF = QPointF()
        self.isMoving : bool = False
#
# editor-new-shape class
#
# stores information about when a new shape is created
#
class EditorNewShape:
    def __init__(self):
        self.shape : Shape = None
        self.anchor_point : QPointF = None

    def draw(self, painter : QPainter):
        self.shape.draw(painter)
#
# editor-edit-shape class
#
# stores information about when an existing shape is edited
#
class EditorEditShape:
    def __init__(self):
        self.shape : Shape = None

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

        self.state : EditorState = EditorState.NONE

        self.scene : EditorScene = EditorScene()
        self.camera : EditorCamera = EditorCamera(dimensions)
        self.newshape : EditorNewShape = EditorNewShape()
        self.editshape : EditorEditShape = EditorEditShape()

        self.clear()
    #
    # manages the current state of the editor with every component
    # for EDIT_EXISTING_SHAPE and ADD_NEW_SHAPE state-values a shape should be provided
    #
    def setState(self, state : EditorState, shape : Shape | None = None) -> None:
        self.state = state
        if (self.state == EditorState.ADD_NEW_SHAPE):
            self.newshape.shape = shape
        elif (self.state == EditorState.EDIT_EXISTING_SHAPE):
            self.editshape.shape = shape


    def paintEvent(self, event : QPaintEvent):
        painter : QPainter = QPainter(self)
        scene_painter : QPainter = QPainter(self.image)
        scene_painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        self.camera.updateTransform()
        scene_painter.setTransform(self.camera.transform)
        self.scene.draw(scene_painter, self.image)
        
        if (self.state == EditorState.ADD_NEW_SHAPE):
            self.newshape.draw(scene_painter)
        
        painter.drawImage(0, 0, self.image)

        scene_painter.end()
        painter.end()

    def mousePressEvent(self, event : QMouseEvent) -> None:
        if (self.state == EditorState.ADD_NEW_SHAPE):
            self.editshape.shape.showBoundingBox = False
            self.setCursor(Qt.CursorShape.CrossCursor)
            self.anchor_point = self.camera.mapToWorld(Utility.toQPointF(event.pos()))
        elif (self.state == EditorState.SCROLL_VIEWPORT):
            self.editshape.shape.showBoundingBox = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.camera.anchorPoint = Utility.toQPointF(event.pos())
            self.camera.anchorViewPoint = self.camera.topLeft
            self.camera.isMoving = True
        elif (self.state == EditorState.NONE):
            for shape in self.scene.attachedShapes:
                if (Utility.PointInRect(self.camera.mapToWorld(Utility.toQPointF(event.pos())), shape.boundingBox)):
                    self.editshape.shape = shape
                    shape.showBoundingBox = True
                    self.state = EditorState.EDIT_EXISTING_SHAPE
                    break
        elif (self.state == EditorState.EDIT_EXISTING_SHAPE):
            found : bool = False
            for shape in self.scene.attachedShapes:
                if (Utility.PointInRect(self.camera.mapToWorld(Utility.toQPointF(event.pos())), shape.boundingBox)):
                    self.editshape.shape.showBoundingBox = False
                    self.editshape.shape = shape
                    shape.showBoundingBox = True
                    found = True
                    break
            if not found and not (self.editshape.shape is None):
                self.editshape.shape.showBoundingBox = False
                self.editshape.shape = None
                self.state = EditorState.NONE
        self.update()


    def mouseReleaseEvent(self, event : QMouseEvent):
        if (self.state == EditorState.ADD_NEW_SHAPE):
            self.setCursor(Qt.CursorShape.ArrowCursor)
            self.scene.attach_object(self.newshape.shape)
            self.state = EditorState.NONE
        elif (self.state == EditorState.SCROLL_VIEWPORT):
            self.camera.isMoving = False 


    def mouseMoveEvent(self, event : QMouseEvent):
        if (self.state == EditorState.ADD_NEW_SHAPE):
            delta : QSizeF = self.camera.mapToWorld(Utility.toQPointF(event.pos())) - self.anchor_point
            self.newshape.shape.center = self.anchor_point + 0.5 * delta
            self.newshape.shape.size = Utility.toQSizeF(delta)
        elif (self.state == EditorState.SCROLL_VIEWPORT):
            if (self.camera.isMoving):
                self.camera.topLeft = self.camera.anchorViewPoint + self.camera.mapToWorld(self.camera.anchorPoint) - self.camera.mapToWorld(Utility.toQPointF(event.pos()))

        self.update()

    def wheelEvent(self, event : QWheelEvent):
        if (self.state == EditorState.SCROLL_VIEWPORT):
            if (event.angleDelta().y() > 0):
                self.camera.zoomFactor = Utility.Clamp(self.camera.zoomFactor + 0.05, 0.5, 1.75)
            else:
                self.camera.zoomFactor = Utility.Clamp(self.camera.zoomFactor - 0.05, 0.5, 1.75)
            self.camera.zoom(self.camera.zoomFactor)
        self.update()

    def clear(self, color : QColor = QColor(255, 255, 255)):
        self.scene.clear()
        self.camera.topLeft = QPointF(0.0, 0.0)
        self.camera.zoomFactor = 1.0
        self.update()