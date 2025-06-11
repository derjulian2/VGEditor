
from Shapes import Shape, Ellipse

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
# import all editor-modules
#
from Editor.Camera import Camera
from Editor.Scene import Scene
from Editor.NewShape import NewShape
from Editor.EditShape import EditShape
from Editor.GroupShapes import GroupShapes
#
# editorstate enum
#
# describes the user-interaction-state that the editor is in
#
class EditorState(Enum):
    SCROLL_CAMERA = 1,  # active when the user is moving around the scene
    NEW_GROUP_EDIT  = 2,  # active when the user is editing/grouping/adding shapes
#
# canvas widget class
#
# custom qt-widget for drawing vector-graphic-shapes
# to an RGB32 image and rendering it to a window
#
# here all other editor-functionality bundles together into one canvas-widget
#
class Canvas(QWidget):
    def __init__(self, parent : QWidget, dimensions : QSize) -> None:
        super().__init__(parent)
        self.setMinimumSize(dimensions)

        self.image : QImage = QImage(dimensions, QImage.Format_RGB32)

        self.state : EditorState = EditorState.NEW_GROUP_EDIT

        # components of the editor-logic
        self.scene : Scene = Scene()
        self.camera : Camera = Camera(self, dimensions)
        self.newShape : NewShape = NewShape(self, self.camera, self.scene)
        self.editShape : EditShape = EditShape(self, self.camera, self.scene)
        self.groupShapes : GroupShapes = GroupShapes(self.editShape)

        self.setState(EditorState.NEW_GROUP_EDIT)

    def paintEvent(self, event : QPaintEvent) -> None:
        painter : QPainter = QPainter(self)
        scene_painter : QPainter = QPainter(self.image)
        scene_painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        self.camera.updateTransform()
        scene_painter.setTransform(self.camera.transform)

        self.scene.update()    
        self.scene.draw(scene_painter, self.image)
    
        self.editShape.draw(scene_painter)

        painter.drawImage(0, 0, self.image)

        scene_painter.end()
        painter.end()

    def setState(self, state : EditorState) -> None:
        self.state = state
        if (self.state == EditorState.NEW_GROUP_EDIT):
            self.camera.enabled = False
            self.newShape.enabled = True
            self.editShape.enabled = True
            self.groupShapes.enabled = True
        elif (self.state == EditorState.SCROLL_CAMERA):
            self.camera.enabled = True
            self.newShape.enabled = False
            self.editShape.enabled = False
            self.groupShapes.enabled = False

    def mousePressEvent(self, event : QMouseEvent) -> None:
        self.camera.mousePressEvent(event)
        self.newShape.mousePressEvent(event)
        self.editShape.mousePressEvent(event)
        self.groupShapes.mousePressEvent(event)
        self.update()

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        self.camera.mouseReleaseEvent(event)
        self.newShape.mouseReleaseEvent(event)
        self.editShape.mouseReleaseEvent(event)
        self.groupShapes.mouseReleaseEvent(event)

    def mouseMoveEvent(self, event : QMouseEvent) -> None:
        self.camera.mouseMoveEvent(event)
        self.newShape.mouseMoveEvent(event)
        self.editShape.mouseMoveEvent(event)
        self.groupShapes.mouseMoveEvent(event)
        self.update()

    def wheelEvent(self, event : QWheelEvent) -> None:
        self.camera.wheelEvent(event)
        self.update()

    def clear(self, color : QColor = QColor(255, 255, 255)) -> None:
        self.scene.clear()
        self.camera.topLeft = QPointF(0.0, 0.0)
        self.camera.zoomFactor = 1.0
        self.update()