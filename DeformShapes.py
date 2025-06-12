
from Shapes import Triangle
from PySide6.QtCore import QRectF, QSizeF, QPointF
from PySide6.QtWidgets import QDialog
from math import sin, cos, pi, radians, degrees
#
# deform-shapes-dialog class
#
# used to configure how a shape is deformed and in what detail
#
class DeformShapeDialog(QDialog):
    def __init__(self):
        pass

#
# subdivides a triangle into four smaller triangles along the center points at the sides
#
def Subdivide(triangle : Triangle) -> list[Triangle]:
    # alias vertices
    a_v : QPointF = triangle.Vertices[0].__copy__()
    b_v : QPointF = triangle.Vertices[1].__copy__()
    c_v : QPointF = triangle.Vertices[2].__copy__()
    # determine centers of triangle sides
    center_ac : QPointF = a_v + 0.5 * (c_v - a_v)
    center_bc : QPointF = b_v + 0.5 * (c_v - b_v)
    center_ab : QPointF = a_v + 0.5 * (b_v - a_v)
    # span new triangles between vertices and new points
    return [ Triangle([ a_v, center_ab, center_ac ]),
             Triangle([ b_v, center_bc, center_ab ]),
             Triangle([ c_v, center_bc, center_ac ]),
             Triangle([ center_ab, center_bc, center_ac ])]
#
# deforms a list of triangles along a sine wave with parameters a, w and o for amplitude, width and offset
#
# f(x) = a * sin(2pi * w * x + o) is essentially added to each point of every triangle in 'triangles'
#
def Deformation(triangles : list[Triangle], amplitude : float, width : float, offset : float) -> list[Triangle]:
    result : list[Triangle] = []
    f = lambda y : amplitude * sin(radians(2 * pi * width * y + offset)) # why in radians?
    for triangle in triangles:
        result.append(Triangle([ QPointF(triangle.Vertex(0).x(), triangle.Vertex(0).y() + f(triangle.Vertex(0).x())),
                                 QPointF(triangle.Vertex(1).x(), triangle.Vertex(1).y() + f(triangle.Vertex(1).x())),
                                 QPointF(triangle.Vertex(2).x(), triangle.Vertex(2).y() + f(triangle.Vertex(2).x()))]))
    return result