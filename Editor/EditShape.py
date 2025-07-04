
from PySide6.QtWidgets import QWidget, QDialog
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtCore import QPointF, QSizeF, QRectF

from Editor.Shapes.Shape import Shape
from Editor.Scene import Scene 
from Editor.Camera import Camera

from enum import Enum

import Utility
#
# edit-shape-dialog class
#
# used to reconfigure attributes of existing shapes
#
class EditShapeDialog(QDialog):
    def __init__(self):
        pass
#
# click-area for handling translate-edit-operations
#
class TranslateArea:
    def __init__(self, camera : Camera):
        self.camera : Camera = camera
        self.area : QRectF = QRectF()
        self.clicked : bool = False
        self.anchorPoint : QPointF = QPointF()
        self.shapeAnchorPoint  : QPointF = QPointF()

    def mousePressEvent(self, event : QMouseEvent, shape : Shape) -> None:
        mouseClickPoint : QPointF = self.camera.view.mapToWorld(Utility.toQPointF(event.pos()))
        if (Utility.PointInRect(mouseClickPoint, self.area)):
            self.clicked = True
            self.anchorPoint = mouseClickPoint
            self.shapeAnchorPoint = shape.topLeft

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        self.clicked = False

    def mouseMoveEvent(self, event : QMouseEvent, shape : Shape) -> None:
        delta : QPointF = self.camera.view.mapToWorld(Utility.toQPointF(event.pos())) - self.anchorPoint
        shape.moveTo(self.shapeAnchorPoint) # move to anchor point
        shape.translate(delta) # move about delta
#
# enum to describe what corner a ScaleArea acts upon
#
class ScaleAreaMode(Enum):
    TOPLEFT = 1
    TOPRIGHT = 2
    BOTTOMLEFT = 3
    BOTTOMRIGHT = 4
#
# click-area for handling scale-edit-operations
#
class ScaleArea:
    def __init__(self, camera : Camera, mode : ScaleAreaMode):
        self.camera : Camera = camera
        self.area : QRectF = QRectF()
        self.clicked : bool = False
        self.anchorPoint : QPointF = QPointF()
        self.shapeAnchorPoint  : QPointF = QPointF()
        self.mode : ScaleAreaMode = mode

    def mousePressEvent(self, event : QMouseEvent, shape : Shape) -> None:
        mouseClickPoint : QPointF = self.camera.view.mapToWorld(Utility.toQPointF(event.pos()))
        if (Utility.PointInRect(mouseClickPoint, self.area)):
            self.clicked = True
            self.anchorPoint = mouseClickPoint
            if (self.mode == ScaleAreaMode.TOPLEFT):
                self.shapeAnchorPoint = shape.topLeft
            elif (self.mode == ScaleAreaMode.TOPRIGHT):
                self.shapeAnchorPoint = shape.topRight
            elif (self.mode == ScaleAreaMode.BOTTOMLEFT):
                self.shapeAnchorPoint = shape.bottomLeft
            elif (self.mode == ScaleAreaMode.BOTTOMRIGHT):
                self.shapeAnchorPoint = shape.bottomRight

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        self.clicked = False

    def mouseMoveEvent(self, event : QMouseEvent, shape : Shape) -> None:
        delta : QPointF = self.camera.view.mapToWorld(Utility.toQPointF(event.pos())) - self.anchorPoint
        if (self.mode == ScaleAreaMode.TOPLEFT):
            shape.topLeft = self.shapeAnchorPoint + delta
        elif (self.mode == ScaleAreaMode.TOPRIGHT):
            shape.topRight = self.shapeAnchorPoint + delta
        elif (self.mode == ScaleAreaMode.BOTTOMLEFT):
            shape.bottomLeft = self.shapeAnchorPoint + delta
        elif (self.mode == ScaleAreaMode.BOTTOMRIGHT):
            shape.bottomRight = self.shapeAnchorPoint + delta
        
from Editor.CanvasComponent import CanvasComponent
## editor-edit-shape class
#
# stores information and logic about when an existing shape is edited
#
class EditShape(CanvasComponent):
    def __init__(self, parent : QWidget, camera : Camera, scene : Scene) -> None:
        super().__init__()
        self.parent : QWidget = parent
        self.camera : Camera = camera
        self.scene : Scene = scene

        self.translateArea : TranslateArea = TranslateArea(camera)
        self.scaleAreas : list[ScaleArea] = [ ScaleArea(camera, ScaleAreaMode.TOPLEFT), 
                                              ScaleArea(camera, ScaleAreaMode.TOPRIGHT), 
                                              ScaleArea(camera, ScaleAreaMode.BOTTOMRIGHT), 
                                              ScaleArea(camera, ScaleAreaMode.BOTTOMLEFT)]

        self.shape : Shape = None
        self.anchor_point : QPointF = None
        self.dragging : bool = False

    def disable(self) -> None:
        super().disable()
        self.dragging = False
        if not (self.shape is None):
            self.shape.__show_bounding_box__ = False
        self.shape = None

    def __find_clicked_shape__(self, clickPoint : QPointF) -> Shape | None:
        for shape in reversed(self.scene.attachedShapes):
            if (Utility.PointInRect(clickPoint, shape.boundingBox)):
                return shape
        return None

    def draw(self, painter : QPainter) -> None:
        if (self.enabled and self.active):
            if not (self.shape is None):
                painter.setPen(QPen(Shape.boundingBoxColor, Shape.boundingBoxWidth))
                painter.drawRect(self.translateArea.area)
                for scaleArea in self.scaleAreas:
                    painter.drawRect(scaleArea.area)

    def __update_edit_areas__(self) -> None:
        self.translateArea.area = QRectF(self.shape.center - 0.1 * Utility.toQPointF(self.shape.size), 0.2 * self.shape.size)
        self.scaleAreas[0].area = QRectF(self.shape.center + 0.5 * QPointF(-self.shape.size.width(), -self.shape.size.height()), 0.2 * self.shape.size)
        self.scaleAreas[1].area = QRectF(self.shape.center + 0.5 * QPointF(self.shape.size.width() - 0.4 * self.shape.size.width(), -self.shape.size.height()), 0.2 * self.shape.size)
        self.scaleAreas[2].area = QRectF(self.shape.center + 0.5 * QPointF(self.shape.size.width() - 0.4 * self.shape.size.width(), self.shape.size.height() - 0.4 * self.shape.size.height()), 0.2 * self.shape.size)
        self.scaleAreas[3].area = QRectF(self.shape.center + 0.5 * QPointF(-self.shape.size.width(), self.shape.size.height() - 0.4 * self.shape.size.height()), 0.2 * self.shape.size)

    def mousePressEvent(self, event : QMouseEvent) -> None:
        if (self.enabled):
            mouseClickPoint : QPointF = self.camera.view.mapToWorld(Utility.toQPointF(event.pos()))
            # differentiate between 'a shape is selected' and 'no shape is selected'
            if (self.shape is None):
                clickedShape : Shape | None = self.__find_clicked_shape__(mouseClickPoint)
                self.shape = clickedShape
                if not (self.shape is None):
                    self.shape.__show_bounding_box__ = True
                    self.active = True
                    self.scene.moveToFront(self.shape)
                    self.__update_edit_areas__()
            else:
                if not (Utility.PointInRect(mouseClickPoint, self.shape.boundingBox)):
                    self.active = False
                    self.shape.__show_bounding_box__ = False
                    self.shape = None
                else:
                    self.translateArea.mousePressEvent(event, self.shape)
                    for scaleArea in self.scaleAreas:
                        scaleArea.mousePressEvent(event, self.shape)

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        if (self.enabled and self.active):
            if (self.translateArea.clicked):
                self.translateArea.mouseReleaseEvent(event)
            for scaleArea in self.scaleAreas:
                if (scaleArea.clicked):
                    scaleArea.mouseReleaseEvent(event)
    
    def mouseMoveEvent(self, event : QMouseEvent) -> None:
        if (self.enabled and self.active):
            if (self.translateArea.clicked):
                self.translateArea.mouseMoveEvent(event, self.shape)
            for scaleArea in self.scaleAreas:
                if (scaleArea.clicked):
                    scaleArea.mouseMoveEvent(event, self.shape)
            self.__update_edit_areas__()