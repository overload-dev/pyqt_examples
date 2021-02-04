from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5 import QtOpenGL

import OpenGL.GL as gl
from OpenGL import GLU
from OpenGL.arrays import vbo
import numpy as np

import sys

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QSlider


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)

        self.resize(300, 300)
        self.setWindowTitle('Hello OpenGL App')

        self.glWidget = GLWidget(self)
        self.initGUI()
        
        # 렌더링 주기 설정
        timer = QtCore.QTimer(self)
        timer.setInterval(20)  # period, in milliseconds
        timer.timeout.connect(self.glWidget.updateGL)
        timer.start()

    def initGUI(self):
        central_widget = QWidget()
        gui_layout = QVBoxLayout()
        central_widget.setLayout(gui_layout)

        self.setCentralWidget(central_widget)

        gui_layout.addWidget(central_widget)
        gui_layout.addWidget(self.glWidget)

        sliderX = QSlider(QtCore.Qt.Horizontal)
        sliderX.valueChanged.connect(lambda val: self.glWidget.setRotX(val * 2))

        sliderY = QSlider(QtCore.Qt.Horizontal)
        sliderY.valueChanged.connect(lambda val: self.glWidget.setRotY(val * 2))

        sliderZ = QSlider(QtCore.Qt.Horizontal)
        sliderZ.valueChanged.connect(lambda val: self.glWidget.setRotZ(val * 2))

        gui_layout.addWidget(sliderX)
        gui_layout.addWidget(sliderY)
        gui_layout.addWidget(sliderZ)


class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)
        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(0, 0, 255))
        gl.glEnable(gl.GL_DEPTH_TEST)

        self.initGeometry()

        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0

    def setRotX(self, val):
        self.rotX = val

    def setRotY(self, val):
        self.rotY = val

    def setRotZ(self, val):
        self.rotZ = val

    def resizeGL(self, width, height):
        # 그리기 창 크기 정의
        gl.glViewport(0, 0, width, height)
        # 그래픽 모드, 투영, 불투명, 폴리곤 등...
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        aspect = width / float(height)

        # 원근 및 시점 정의
        GLU.gluPerspective(45.0, aspect, 1.0, 100.0)

        # 일반적으로 GL_PROJECT외 모드 외에서 사용안함
        gl.glMatrixMode(gl.GL_MODELVIEW)

    # 렌더링 처리
    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        gl.glPushMatrix()             # push the current matrix to the current stack 변환 행렬 복사, 현재 행렬에 Push에 사용

        gl.glTranslate(0.0, 0.0, -50.0)     # 매트릭스 좌표 설정, z 축으로 50만큼 깊이를 준다.
        gl.glScale(20.0, 20.0, 20.0)        # 매트릭스 크기

        gl.glRotate(self.rotX, 1.0, 0.0, 0.0)
        gl.glRotate(self.rotY, 0.0, 1.0, 0.0)
        gl.glRotate(self.rotZ, 0.0, 0.0, 1.0)
        gl.glTranslate(-0.5, -0.5, -0.5)    # 중심점을 정육면체 한 가운데로 변환

        gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
        gl.glEnableClientState(gl.GL_COLOR_ARRAY)

        gl.glVertexPointer(3, gl.GL_FLOAT, 0, self.vertVBO)     # 선언 이후 GPU가 vertex 데이터에 액세스 가능
        gl.glColorPointer(3, gl.GL_FLOAT, 0, self.colorVBO)    # 선언 이후 GPU가 color 데이터에 액세스 가능

        # 렌더링 호출
        gl.glDrawElements(gl.GL_QUADS, len(self.cubeIdxArray), gl.GL_UNSIGNED_INT, self.cubeIdxArray)

        gl.glDisableClientState(gl.GL_VERTEX_ARRAY)
        gl.glDisableClientState(gl.GL_COLOR_ARRAY)

        gl.glPopMatrix()    # restore the previous modelview matrix
        
    def initGeometry(self):
        # cube Vertex buffer object Array
        #     h---------g       a = [0.0, 0.0, 0.0]       e = [0.0, 0.0, 1.0]
        #    / |       /|       b = [1.0, 0.0, 0.0]       f = [1.0, 0.0, 1.0]
        #   /  |      / |       c = [1.0, 1.0, 0.0]       g = [1.0, 1.0, 1.0]
        #  d---|-----c  |       d = [0.0, 1.0, 0.0]       h = [0.0, 1.0, 1.0]
        #  |   e-----|--f
        #  |  /      | /
        #  a---------b

        self.cubeVtxArray = np.array(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [1.0, 1.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 1.0, 1.0],
             [0.0, 1.0, 1.0]])

        self.vertVBO = vbo.VBO(np.reshape(self.cubeVtxArray, (1, -1)).astype(np.float32))
        self.vertVBO.bind()

        self.cubeClrArray = np.array(
            [[0.0, 0.0, 0.0],
             [1.0, 0.0, 0.0],
             [1.0, 1.0, 0.0],
             [0.0, 1.0, 0.0],
             [0.0, 0.0, 1.0],
             [1.0, 0.0, 1.0],
             [1.0, 1.0, 1.0],
             [0.0, 1.0, 1.0]])
        self.colorVBO = vbo.VBO(np.reshape(self.cubeClrArray, (1, -1)).astype(np.float32))
        self.colorVBO.bind()

        # 6 spaces color
        self.cubeIdxArray = np.array(
            [0, 1, 2, 3,
             3, 2, 6, 7,
             1, 0, 4, 5,
             2, 1, 5, 6,
             0, 3, 7, 4,
             7, 6, 5, 4])


if __name__ == '__main__':

    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()

    sys.exit(app.exec_())
