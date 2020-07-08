import math
import vtk
import sys
import matplotlib.pyplot as plt
import numpy as np
import beam_vtk as bvtk
from collections import defaultdict
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

actors = defaultdict(list)

# @ben: here are alternative mode coefficients you can try out:
#       0.6 , 1.5,  2.5 , 3.5
x_vals = range(21)
# x_vals = [0, 1, 2, 3]
t_vals = np.linspace(0, 4 * math.pi, 40).tolist()
t_val_step = (2 * math.pi) / 40
current_t_val = 0

mode = 2.5
mode_max = 3.5
omega = 1
is_playing = True

timer = QtCore.QTimer()
is_transparent = True

vtk_widget: QVTKRenderWindowInteractor


class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()

    def leftButtonPressEvent(self, obj, event):
        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())

        # get the new
        self.NewPickedActor = picker.GetActor()

        # If something was selected
        if self.NewPickedActor:
            # If we picked something before, reset its property
            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)

            # Save the property of the picked actor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())
            # Highlight the picked actor by changing its properties
            self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)

            actor_center = self.NewPickedActor.GetCenter()
            actor_x = actor_center[0]
            actor_y = actor_center[1]
            actor_z = actor_center[2]

            global vtk_widget
            msgBox = QtWidgets.QMessageBox()
            msgBox.setText("X: {}\nY: {}\nZ: {}".format(actor_x, actor_y, actor_z))

            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setWindowTitle("Node Info")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Cancel)

            returnValue = msgBox.exec()

            # save the last picked actor
            self.LastPickedActor = self.NewPickedActor

        self.OnLeftButtonDown()
        return


class MainWindow(QtWidgets.QMainWindow):
    is_playing: bool = False
    renderer = None
    interactor = None
    window = None
    mode_changed_signal = QtCore.pyqtSignal(float)
    omega_changed_signal = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        global vtk_widget

        self.frame = QtWidgets.QFrame()

        self.main_vlayout = QtWidgets.QVBoxLayout()
        vtk_widget = QVTKRenderWindowInteractor(self.frame)
        self.main_vlayout.addWidget(vtk_widget)

        # Start setup mode slider layout
        self.mode_slider_layout = QtWidgets.QHBoxLayout()

        self.m_slider_label = QtWidgets.QLabel()
        self.m_slider_label.setText("Mode: ")
        self.m_slider_label.setAlignment(QtCore.Qt.AlignLeft)

        self.mode_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.mode_slider.setMinimum(0)
        self.mode_slider.setMaximum(100)
        self.mode_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.mode_slider.setTickInterval(1)

        normalized_val = (mode / mode_max) * 100
        self.mode_slider.setValue(int(normalized_val))

        self.mode_slider.valueChanged.connect(self.mode_value_change)

        self.mode_slider_layout.addWidget(self.m_slider_label)
        self.mode_slider_layout.addWidget(self.mode_slider)

        self.main_vlayout.addLayout(self.mode_slider_layout)
        # End setup mode slider layout

        # Start setup omega slider layout
        self.omega_slider_layout = QtWidgets.QHBoxLayout()

        self.o_slider_label = QtWidgets.QLabel()
        self.o_slider_label.setText("Omega: ")
        self.o_slider_label.setAlignment(QtCore.Qt.AlignLeft)

        self.omega_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.omega_slider.setMinimum(0)
        self.omega_slider.setMaximum(10)
        self.omega_slider.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.omega_slider.setTickInterval(1)

        self.omega_slider.valueChanged.connect(self.omega_value_change)

        self.omega_slider_layout.addWidget(self.o_slider_label)
        self.omega_slider_layout.addWidget(self.omega_slider)

        self.main_vlayout.addLayout(self.omega_slider_layout)
        # End setup omega slider layout

        self.button = QtWidgets.QPushButton("Pause")
        self.button.pressed.connect(self.play_pause_button)

        self.main_vlayout.addWidget(self.button)

        self.renderer = vtk.vtkRenderer()
        vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = vtk_widget.GetRenderWindow().GetInteractor()
        self.window = vtk_widget.GetRenderWindow()

        self.frame.setLayout(self.main_vlayout)
        self.setCentralWidget(self.frame)

        style = MouseInteractorHighLightActor()
        style.SetDefaultRenderer(self.renderer)
        self.interactor.SetInteractorStyle(style)

        self.interactor.Initialize()
        self.interactor.Start()
        self.show()

    def play_pause_button(self):
        self.is_playing = not self.is_playing
        global timer
        if self.is_playing:
            self.button.setText("Pause")
            timer.start(50)
        else:
            self.button.setText("Play")
            timer.stop()

    def add_slot(self, vtk_update):
        self.mode_changed_signal.connect(vtk_update.set_mode)
        self.omega_changed_signal.connect(vtk_update.set_omega)

    def mode_value_change(self, value):
        global mode
        mode = (value / 100) * mode_max
        self.mode_changed_signal.emit(mode)
        print("mode changed: ", mode)

    def omega_value_change(self, value):
        global omega
        omega = value
        self.omega_changed_signal.emit(omega)
        print("omega changed: ", omega)


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
    N -= 1

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()

    # bvtk.Node and bvtk.Line are custom objects to make reuse of mappings/actors
    # convenient and less messy.
    nodes = [bvtk.Node() for i in range(N)]

    y = beam_deflection(10)  # grabbing an arbitrary time to create deflected beam state
    for i in range(N):

        if i < (N - 1):
            # Updates position ahead of time to render next node height
            nodes[i + 1].update_position(x[i + 1], y[i + 1], 0)
            next_node = nodes[i + 1]
        else:
            next_node = nodes[i - 1]

        # Generates all node specific actors and adds to renderer
        nodes[i].add_poly_actor_to_renderer(main_window.renderer, next_node, x[i], y[i])

    main_window.window.Render()

    cb = bvtk.vtkUpdate(main_window.window, 0, nodes)
    main_window.add_slot(cb)
    # main_window.interactor.AddObserver('TimerEvent', cb.execute)
    # cb.timerId = main_window.interactor.CreateRepeatingTimer(150)
    timer.timeout.connect(cb.execute)
    timer.start(50)

    # # Sign up to receive TimerEvent
    main_window.renderer.ResetCamera()

    sys.exit(app.exec_())


if __name__ == "__main__":
    # generate_plot(t_vals, x_vals)
    generate_vtk(t_vals, x_vals)
