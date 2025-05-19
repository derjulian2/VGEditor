from PySide6.QtCore import QSize, QSizeF, QPoint, QPointF
from PySide6.QtGui import QVector2D
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

def Clamp(val : float, min : float, max : float):
    if (min > max or max < min):
        raise AttributeError("min and max mismatch")
    if (val > max):
        return max
    elif (val < min):
        return min
    return val