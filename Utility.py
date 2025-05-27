from PySide6.QtCore import QSize, QSizeF, QPoint, QPointF, QRectF
from PySide6.QtGui import QVector2D
from math import isnan
#
# utility conversion functions between Qt's
# vectors, points and sizes
#
def toQSizeF(other : QVector2D | QPointF | QPoint | QSize):
    if (isinstance(other, QVector2D) or isinstance(other, QPointF) or isinstance(other, QPoint)):
        return QSizeF(float(other.x()), float(other.y()))
    elif (isinstance(other, QSize)):
        return QSizeF(float(other.width()), float(other.height()))
    else:
        raise TypeError("false type passed to QSizeFCast")
    
def toQPointF(other : QVector2D | QPoint | QSizeF | QSize):
    if (isinstance(other, QVector2D) or isinstance(other, QPoint)):
        return QPointF(float(other.x()), float(other.y()))
    elif (isinstance(other, QSize) or isinstance(other, QSizeF)):
        return QPointF(float(other.width()), float(other.height()))
    else:
        raise TypeError("false type passed to QPointFCast")

def toQVector2D(other : QPointF | QPoint | QSizeF | QSize) -> QVector2D:
    if (isinstance(other, QPointF) or isinstance(other, QPoint)):
        return QVector2D(float(other.x()), float(other.y()))
    elif (isinstance(other, QSize) or isinstance(other, QSizeF)):
        return QVector2D(float(other.width()), float(other.height()))
    else:
        raise TypeError("false type passed to QVector2DCast")
#
# clamp a value to a given range
#
def Clamp(val : float, min : float, max : float):
    if (min > max or max < min):
        raise AttributeError("min and max mismatch")
    if (val > max):
        return max
    elif (val < min):
        return min
    return val
#
# determines if a point is within a given rectangle
#
def PointInRect(p : QPointF, rect : QRectF) -> bool:
    if (p.x() >= rect.x() and p.x() <= rect.x() + rect.width() and p.y() >= rect.y() and p.y() <= rect.y() + rect.height()):
        return True
    return False
#
# retrieve the sign of a number. returns 1 in case of 0, raises error if NaN
#
def sign(f : float) -> int:
    if (isnan(f)):
        raise AttributeError("float was NaN")
    if (f >= 0.0):
        return 1
    return -1