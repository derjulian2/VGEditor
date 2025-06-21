
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
from Editor.CanvasComponent import CanvasComponent

import os
import xml.etree.ElementTree as XMLTree

#
# editorstate enum
#
# describes the user-interaction-state that the editor is in
#
class EditorState(Enum):
    SCROLL_CAMERA = 1,  # active when the user is moving around the scene
    NEW           = 2,  # active when the user is adding shapes
    EDIT          = 3,  # active when the user is editing shapes
    GROUP         = 4   # active when the user is grouping together shapes
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

        self.state : EditorState = EditorState.EDIT

        # components of the editor-logic
        self.scene : Scene = Scene()
        
        self.camera : Camera = Camera(self, dimensions)
        self.newShape : NewShape = NewShape(self, self.camera, self.scene)
        self.editShape : EditShape = EditShape(self, self.camera, self.scene)
        self.groupShapes : GroupShapes = GroupShapes(self, self.camera, self.scene)

        self.components : list[CanvasComponent] = [ self.camera,
                                                    self.newShape,
                                                    self.editShape,
                                                    self.groupShapes]

        self.setState(EditorState.EDIT)

    def paintEvent(self, event : QPaintEvent) -> None:
        painter : QPainter = QPainter(self)
        scene_painter : QPainter = QPainter(self.image)
        scene_painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        self.camera.view.updateTransform()
        scene_painter.setTransform(self.camera.view.transform)

        self.scene.update()    
        self.scene.draw(scene_painter, self.image)
    
        self.editShape.draw(scene_painter)

        painter.drawImage(0, 0, self.image)

        scene_painter.end()
        painter.end()

    def setState(self, state : EditorState) -> None:
        self.state = state
        for component in self.components:
            component.disable()
        if (self.state == EditorState.NEW):
            self.newShape.enable()
        elif (self.state == EditorState.EDIT):
            self.editShape.enable()
        elif (self.state == EditorState.SCROLL_CAMERA):
            self.camera.enable()
        elif (self.state == EditorState.GROUP):
            self.groupShapes.enable()

    def mousePressEvent(self, event : QMouseEvent) -> None:
        for component in self.components:
            component.mousePressEvent(event)
        self.update()

    def mouseReleaseEvent(self, event : QMouseEvent) -> None:
        for component in self.components:
            component.mouseReleaseEvent(event)
        self.update()

    def mouseMoveEvent(self, event : QMouseEvent) -> None:
        for component in self.components:
            component.mouseMoveEvent(event)
        self.update()

    def wheelEvent(self, event : QWheelEvent) -> None:
        for component in self.components:
            component.wheelEvent(event)
        self.update()

    def clear(self, color : QColor = QColor(255, 255, 255)) -> None:
        self.scene.clear()
        self.camera.topLeft = QPointF(0.0, 0.0)
        self.camera.zoomFactor = 1.0
        self.update()

    #
    # export a scene to an XML-SVG-file
    #
    # https://de.wikipedia.org/wiki/Scalable_Vector_Graphics
    #
    #
    def exportSceneToSVG(self, file : os.path, title : str, description : str) -> None:
        # required attributes for xml-tree to qualify as svg
        root_svg_attributes : dict[str,str] = { "xmlns" : "http://www.w3.org/2000/svg",
                                                "xmlns:xlink" : "http://www.w3.org/1999/xlink",
                                                "version" : "1.1",
                                                "baseProfile" : "full",
                                                "width" : f"{self.image.size().width()}mm",
                                                "height" : f"{self.image.size().height()}mm",
                                                "viewBox" : f"{self.camera.view.topLeft.x()} {self.camera.view.topLeft.y()} {self.camera.view.viewportArea.width()} {self.camera.view.viewportArea.height()}"}
        
        root_svg : XMLTree.Element = XMLTree.Element("svg", root_svg_attributes)
        # title and description
        title_tag : XMLTree.Element = XMLTree.Element("title")
        descr_tag : XMLTree.Element = XMLTree.Element("desc")
        title_tag.text = title
        descr_tag.text = description

        root_svg.append(title_tag)
        root_svg.append(descr_tag)
        # add info about all shapes
        for shape in self.scene.attachedShapes:
            root_svg.append(shape.toSVG())
        # print out tree
        tree : XMLTree.ElementTree = XMLTree.ElementTree(root_svg)
        XMLTree.indent(tree, space="\t", level=0)
        tree.write(file, encoding="utf-8", xml_declaration=True)
    #
    # import a scene / a set of shapes using an XML-SVG-file (only supported shapes will be parsed)
    # parameter 'scene' will be mutated (rather than return-value bc Canvas-Scene-object should not change)
    #
    def importShapesFromSVG(scene : Scene, file : os.path) -> None:
        pass