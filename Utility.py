from PySide6.QtCore import QSize, QSizeF, QPoint, QPointF
from PySide6.QtGui import QVector2D

def QSizetoQVector2D(size : QSize) -> QVector2D:
    return QVector2D(float(size.width()), float(size.height()))

def QPointtoQVector2D(point : QPoint) -> QVector2D:
    return QVector2D(float(point.x()), float(point.y()))

def QVector2DtoQPoint(vec : QVector2D) -> QPoint:
    return QPoint(int(vec.x()), int(vec.y()))

def QPointtoQPointF(point : QPoint) -> QPointF:
    return QPointF(float(point.x()), float(point.y()))

def QSizeFtoQPointF(size : QSizeF) -> QPointF:
    return QPointF(float(size.width()), float(size.height()))

def QPointtoQSizeF(point : QPoint) -> QSizeF:
    return QSizeF(float(point.x()), float(point.y()))

def QPointFtoQSizeF(point : QPointF) -> QSizeF:
    return QSizeF(float(point.x()), float(point.y()))
#
# utility conversion function between Qt's
# vectors, points and sizes
#
def QSizeFCast(other : QVector2D | QPointF | QPoint | QSize):
    if (isinstance(other, QVector2D) or isinstance(other, QPointF) or isinstance(other, QPoint)):
        return QSizeF(float(other.x()), float(other.y()))
    elif (isinstance(other, QSize)):
        return QVector2D(float(other.width()), float(other.height()))
    else:
        raise TypeError("false type passed to QSizeFCast")
    
def QPointFCast(other : QVector2D | QPoint | QSizeF | QSize):
    if (isinstance(other, QVector2D) or isinstance(other, QPoint)):
        return QPointF(float(other.x()), float(other.y()))
    elif (isinstance(other, QSize) or isinstance(other, QSizeF)):
        return QPointF(float(other.width()), float(other.height()))
    else:
        raise TypeError("false type passed to QPointFCast")

def QVector2DCast(other : QPointF | QPoint | QSizeF | QSize) -> QVector2D:
    if (isinstance(other, QPointF) or isinstance(other, QPoint)):
        return QVector2D(float(other.x()), float(other.y()))
    elif (isinstance(other, QSize) or isinstance(other, QSizeF)):
        return QVector2D(float(other.width()), float(other.height()))
    else:
        raise TypeError("false type passed to QVector2DCast")

def Clamp(val : float, min : float, max : float):
    if (min > max or max < min):
        raise AttributeError("min and max mismatch")
    if (val > max):
        return max
    elif (val < min):
        return min
    return val