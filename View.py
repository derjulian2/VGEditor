from PySide6.QtGui import (
    QVector2D,  QPainter,       QImage, 
    QColor,     QPaintEvent
)

from PySide6.QtCore import QPointF, QSize
#
# view class
#
# defines what part of a canvas should be displayed
# when Scene.draw() is called
#
# this implementation assumes that the y-axis points up and the x-axis points to the right
#
class View:
    def __init__(self, dimensions: QVector2D, top_left : QVector2D = QVector2D(0, 0)):
        self.dimensions : QVector2D = dimensions
        self.top_left : QVector2D = top_left
    
    # transform passed point from world-coordinates 
    # to view coordinates using the data of the view
    def transform(self, point : QPointF) -> QPointF:
        return QPointF(point.x() - self.top_left.x(), point.y() - self.top_left.y())