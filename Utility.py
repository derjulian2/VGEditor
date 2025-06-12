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
    
def invert2D(v : QPointF | QSizeF | QVector2D) -> QPointF | QSizeF | QVector2D:
    if (isinstance(v, QPointF)):
        return QPointF(1.0 / v.x(), 1.0 / v.y())
    elif (isinstance(v, QVector2D)):
        return QVector2D(1.0 / v.x(), 1.0 / v.y())
    elif (isinstance(v, QSizeF)):
        return QSizeF(1.0 / v.width(), 1.0 / v.height())
    else:
        raise TypeError("false type passed to invert2D")
    
def QSizeFDivide(a : QSizeF, b : QSizeF) -> QSizeF:
    if (b.width() == 0 or b.height() == 0):
        return QSizeF(a.width() / 0.0001, a.height() / 0.0001)
    return QSizeF(a.width() / b.width(), a.height() / b.height())

def QSizeFMultiply(a : QSizeF, b : QSizeF) -> QSizeF:
    return QSizeF(a.width() * b.width(), a.height() * b.height())

def QPointFDivide(a : QPointF, b : QPointF) -> QPointF:
    if (b.x() == 0 or b.y() == 0):
        return QPointF(a.x() / 0.0001, a.x() / 0.0001)
    return QPointF(a.x() / b.x(), a.y() / b.y())

def QPointFMultiply(a : QPointF, b : QPointF) -> QPointF:
    return QPointF(a.x() * b.x(), a.y() * b.y())

def QPointFAbs(p : QPointF) -> QPointF:
    return QPointF(abs(p.x()), abs(p.y()))

def QSizeFAbs(s : QSizeF) -> QSizeF:
    return QSizeF(abs(s.width()), abs(s.height()))

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