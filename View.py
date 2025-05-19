from PySide6.QtGui import (
    QVector2D,  QPainter,       QImage, 
    QColor,     QPaintEvent
)

from PySide6.QtCore import QPointF, QSizeF

import Utility
#
# view class
#
# defines what part of a canvas should be displayed
# when Scene.draw() is called
#
# this implementation assumes that the y-axis points up and the x-axis points to the right
#
# zoom feature is not yet implemented correctly. Zooming will zoom into the origin not the center of the camera
#
class View:
    def __init__(self, viewportSize : QSizeF, viewportArea : QSizeF, center : QPointF = QPointF(0, 0)):
        self.center : QPointF = center
        self.zoomFactor : float = 1.0
        self.viewportSize : QSizeF = viewportSize
        self.viewportArea : QSizeF = viewportArea

    def zoom(self, zoomFactor : float) -> None:
        self.viewportArea = Utility.QSizeFCast(Utility.QVector2DCast(self.viewportSize) * zoomFactor)
    
    #
    # transform passed point from world to screen-coordinates
    #
    def transformPoint(self, point : QPointF) -> QPointF:
        factor : QVector2D = Utility.QVector2DCast(self.viewportArea) / Utility.QVector2DCast(self.viewportSize)
        point_camera_space : QPointF = Utility.QPointFCast((Utility.QVector2DCast(point) * self.zoomFactor) - Utility.QVector2DCast(self.center))
        point_screen_space : QPointF = Utility.QPointFCast((Utility.QVector2DCast(point_camera_space)) * factor)
        return point_screen_space

    #
    # transform passed size or length from world to screen-coordinates
    #
    def transformSize(self, size : QSizeF) -> QSizeF:
        factor : QVector2D = Utility.QVector2DCast(self.viewportArea) / Utility.QVector2DCast(self.viewportSize)
        return Utility.QSizeFCast(Utility.QVector2DCast(size) * self.zoomFactor * factor)
    #
    # inverse operations of the transformPoint() method
    # transforms passed point from screen to world-coordinates
    #
    def transformPointInverse(self, point : QPointF) -> QPointF:
        factor : QVector2D = Utility.QVector2DCast(self.viewportArea) / Utility.QVector2DCast(self.viewportSize)
        point_camera_space : QPointF = Utility.QPointFCast(Utility.QVector2DCast(point) / factor)
        point_world_space : QPointF = Utility.QPointFCast((Utility.QVector2DCast(point_camera_space) + Utility.QVector2DCast(self.center)) / self.zoomFactor)
        return point_world_space

    #
    # inverse operations of the transformSize() method
    # transforms passed size or length from screen to world-coordinates
    #
    def transformSizeInverse(self, size : QSizeF) -> QSizeF:
        factor : QVector2D = Utility.QVector2DCast(self.viewportArea) / Utility.QVector2DCast(self.viewportSize)
        return Utility.QSizeFCast((Utility.QVector2DCast(size) / factor) / self.zoomFactor)