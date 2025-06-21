
from PySide6.QtWidgets import QWidget, QDialog
from PySide6.QtGui import QColor, QMouseEvent, QPainter, QPen
from PySide6.QtCore import QPointF, QSizeF, QRectF
from PySide6.QtCore import Qt

from Editor.Shapes.Shape import Shape
from Editor.Shapes.Aggregate import AggregateShape
from Editor.Scene import Scene 
from Editor.Camera import Camera
from Editor.EditShape import EditShape

import Utility

from Editor.CanvasComponent import CanvasComponent
#
# editor group-shapes class
#
# canvas-component that stores information and logic about grouping 
# together shapes to aggregate shapes
#
class GroupShapes(CanvasComponent):
    def __init__(self, parent : QWidget, camera : Camera, scene : Scene) -> None:
        super().__init__()
        self.parent : QWidget = parent
        self.camera : Camera = camera
        self.scene : Scene = scene
        
        self.selected_shapes : list[Shape] = []

    def disable(self) -> None:
        super().disable()
        if (len(self.selected_shapes)):
            for shape in self.selected_shapes:
                shape.__show_bounding_box__ = False
            self.selected_shapes.clear()
    
    def __find_clicked_shape__(self, clickPoint : QPointF) -> Shape | None:
        for shape in reversed(self.scene.attachedShapes):
            if (Utility.PointInRect(clickPoint, shape.boundingBox)):
                return shape
        return None

    def __group_selected_shapes__(self) -> None:
        #for shape in self.selected_shapes:
        #     self.scene.attachedShapes.remove(shape)
        self.scene.attach_object(AggregateShape(self.selected_shapes))
        self.disable()

    def mousePressEvent(self, event : QMouseEvent) -> None:
        if (self.enabled):
            if (event.button() == Qt.MouseButton.LeftButton):
                mouseClickPoint : QPointF = self.camera.view.mapToWorld(Utility.toQPointF(event.pos()))
                selected_shape : Shape | None = self.__find_clicked_shape__(mouseClickPoint)
                if (selected_shape is None):
                    self.disable()
                else:
                    selected_shape.__show_bounding_box__ = True
                    self.selected_shapes.append(selected_shape)
            elif (event.button() == Qt.MouseButton.RightButton):
                if (len(self.selected_shapes) > 0):
                    self.__group_selected_shapes__()

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        pass

    def mouseMoveEvent(self, event : QMouseEvent) -> None:
        pass