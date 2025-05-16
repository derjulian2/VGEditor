from PySide6.QtCore import QSize, QSizeF, QPoint, QPointF
from PySide6.QtGui import QVector2D

def toQVector2D(size : QSize) -> QVector2D:
    return QVector2D(float(size.width()), float(size.height()))

def toQVector2D(point : QPoint) -> QVector2D:
    return QVector2D(float(point.x()), float(point.y()))

def toQPoint(vec : QVector2D) -> QPoint:
    return QPoint(int(vec.x()), int(vec.y()))