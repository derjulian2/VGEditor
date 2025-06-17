# from UI.Window import Window
# from PySide6.QtWidgets import QApplication

# import sys

# if __name__ == "__main__":

#     app : QApplication = QApplication(sys.argv)

#     main_window : Window = Window(None)
#     main_window.show()
    
#     app.exec()

import xml.etree
import xml.etree.ElementTree as tree

from Editor.Shapes.Primitives import Rectangle, Polygon, QPointF, QSizeF
from Editor.Shapes.Aggregate import AggregateShape
from Editor.Scene import Scene, exportSceneToSVG, QSize, QRect, exampleScene2, exampleScene3


sc : Scene = Scene()

exampleScene2(sc)

exportSceneToSVG(sc, "/home/julian/Projects/University/VGEditor/out.svg", 
                 "mysvg", "descr",
                 QSize(400, 400), QRect(0, 0, 400, 400))

