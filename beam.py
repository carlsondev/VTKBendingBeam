import math
import vtk
import sys
import matplotlib.pyplot as plt
import numpy as np
import beam_vtk as bvtk
from collections import defaultdict
from PyQt5 import QtCore, QtWidgets
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

actors = defaultdict(list)

# @ben: here are alternative mode coefficients you can try out:
#       0.59686 , 1.49418,  2.5 , 3.5
mode = 1.49418
omega = 2
x_vals = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
#x_vals = [0, 1, 2, 3]
t_vals = np.linspace(0, 4 * math.pi, 40).tolist()
t_val_step = (2 * math.pi)/40
current_t_val = 0


class MainWindow(QtWidgets.QMainWindow):
    renderer = None
    interactor = None
    window = None

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        self.frame = QtWidgets.QFrame()

        self.vl = QtWidgets.QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)
        self.vl.addWidget(self.vtkWidget)

        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()
        self.window = self.vtkWidget.GetRenderWindow()

        self.frame.setLayout(self.vl)
        self.setCentralWidget(self.frame)

        self.interactor.Initialize()
        self.interactor.Start()
        self.show()

def displacement(mode, x):
    beta = math.pi * mode
    r = beta * x
    try:
        k = (math.cos(beta) + math.cosh(beta) / (math.sin(beta) + math.sinh(beta)))
        return (math.cosh(r) - math.cos(r) + k * (math.sin(r) - math.sinh(r)))
    except ZeroDivisionError:
        return 0.0

def beam_deflection(t_val):
    return [displacement(mode, pos / x_vals[-1]) * math.sin(omega * t_val) for pos in x_vals]


def generate_plot(t, x):
    for i, time in enumerate(t):
        y = beam_deflection(time)
        plt.figure(1)

        if i == 3:
            plt.plot(x, y, 'bo-')
        else:
            plt.plot(x, y, 'k-', alpha=0.1)

    plt.xlabel('x distance on beam')
    plt.ylabel('y(x,t) displacement')
    plt.grid(True)
    plt.show(block=False)


def generate_vtk(t_vals, x):
    N = len(x)
    N-=1
    app = QtWidgets.QApplication(sys.argv)

    main_window = MainWindow()

    # bvtk.Node and bvtk.Line are custom objects to make reuse of mappings/actors
    # convenient and less messy.
    nodes = [bvtk.Node() for i in range(N)]

    y = beam_deflection(10)  # grabbing an arbitrary time to create deflected beam state
    for i in range(N):

        if i < (N - 1):
            #Updates position ahead of time to render next node height
            nodes[i + 1].update_position(x[i + 1], y[i + 1], 0)
            next_node = nodes[i + 1]
        else:
            next_node = nodes[i-1]

        #Generates all node specific actors and adds to renderer
        nodes[i].add_poly_actor_to_renderer(main_window.renderer, next_node, x[i], y[i])


    main_window.window.Render()

    cb = bvtk.vtkUpdate(main_window.window, 0, nodes)
    # main_window.interactor.AddObserver('TimerEvent', cb.execute)
    # cb.timerId = main_window.interactor.CreateRepeatingTimer(150)

    timer = QtCore.QTimer()
    timer.timeout.connect(cb.execute)
    timer.start(50)

    # # Sign up to receive TimerEvent
    main_window.renderer.ResetCamera()

    sys.exit(app.exec_())


if __name__ == "__main__":

    generate_plot(t_vals, x_vals)
    generate_vtk(t_vals, x_vals)
