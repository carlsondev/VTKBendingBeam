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
node_count = 11
x_vals = range(node_count)
# x_vals = [0, 1, 2, 3]
t_vals = np.linspace(0, 4 * math.pi, 40).tolist()
t_val_step = (2 * math.pi) / 40
current_t_val = 0

mode = 2.5
mode_max = 3.5
omega = 1
is_playing = True

attach_camera_to_node = False
camera_is_attached = False

timer = QtCore.QTimer()
is_transparent = True

vtk_widget: QVTKRenderWindowInteractor
camera = vtk.vtkCamera()

camera_delta_values = [0, 0, 0]
# Index = 0: Not selecting, 1: Selecting Position, 2: Selecting Focal Point
selecting_camera_index = 0
focalActor: vtk.vtkActor
positionActor: vtk.vtkActor

update_slot = None



class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, main_window, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.key_pressed)
        self.main_window = main_window
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()

    def key_pressed(self, renderer, event):
        global camera
        key = self.GetInteractor().GetKeySym()
        azi_step = 2
        ele_step = 2
        if key == "Left":
            camera.Roll(azi_step)
        if key == "Right":
            camera.Roll(-azi_step)
        if key == "Up":
            camera.Elevation(ele_step)
        if key == "Down":
            camera.Elevation(-ele_step)

    def leftButtonPressEvent(self, obj, event):

        global attach_camera_to_node
        global camera_is_attached
        global camera
        global selecting_camera_index
        global positionActor
        global focalActor
        global vtk_widget
        global update_slot

        clickPos = self.GetInteractor().GetEventPosition()

        picker = vtk.vtkPropPicker()
        picker.Pick(clickPos[0], clickPos[1], 0, self.GetDefaultRenderer())

        # get the new actor
        self.NewPickedActor = picker.GetActor()

        # If something was selected
        if self.NewPickedActor:
            # If we picked something before, reset its property
            if self.LastPickedActor:
                self.LastPickedActor.GetProperty().DeepCopy(self.LastPickedProperty)

            # Save the property of the picked actor so that we can
            # restore it next time
            self.LastPickedProperty.DeepCopy(self.NewPickedActor.GetProperty())

            # Allows selection only for nodes
            producer = self.NewPickedActor.GetMapper().GetInputConnection(0, 0).GetProducer()
            if type(producer) is not vtk.vtkSphereSource:
                return

            # Highlight the picked actor by changing its properties
            self.NewPickedActor.GetProperty().SetColor(0.0, 0.0, 1.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)

            if attach_camera_to_node and not camera_is_attached:
                selecting_camera_index += 1
                if selecting_camera_index == 1:
                    # Adding Position Point
                    positionActor = self.NewPickedActor
                    update_slot.set_camera_pos_actor(positionActor, camera)
                    self.main_window.attach_cam_label.setText("Click node to set focal point")
                    return

                if selecting_camera_index == 2:
                    # Adding Focal Point
                    focalActor = self.NewPickedActor
                    self.main_window.attach_cam_label.setText("")

                pos_center = positionActor.GetCenter()
                focal_center = focalActor.GetCenter()
                selecting_camera_index = 0
                camera_is_attached = True
                camera.SetPosition(np.add(pos_center, camera_delta_values))
                camera.SetFocalPoint(focal_center)
                vtk_widget.GetRenderWindow().Render()
                return

            actor_center = self.NewPickedActor.GetCenter()
            actor_x = actor_center[0]
            actor_y = actor_center[1]
            actor_z = actor_center[2]

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
    cam_azimuth_val = 0

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self, parent)

        global vtk_widget

        self.frame = QtWidgets.QFrame()

        self.main_vlayout = QtWidgets.QVBoxLayout()
        vtk_widget = QVTKRenderWindowInteractor(self.frame)
        self.main_vlayout.addWidget(vtk_widget)

        self.setup_mode_slider()
        self.setup_omega_slider()


        self.control_button = QtWidgets.QPushButton("Pause")
        self.control_button.pressed.connect(self.play_pause_button)

        self.main_vlayout.addWidget(self.control_button)


        self.attach_camera_layout = QtWidgets.QHBoxLayout()

        self.attach_camera_button = QtWidgets.QPushButton("Attach Camera To Node")
        self.attach_camera_button.pressed.connect(self.attach_camera)
        self.attach_camera_layout.addWidget(self.attach_camera_button)

        self.attach_cam_label = QtWidgets.QLabel()
        self.attach_cam_label.setText("")
        self.attach_camera_layout.addWidget(self.attach_cam_label)

        self.main_vlayout.addLayout(self.attach_camera_layout)

        self.setup_camera_delta_layout()

        self.reset_button = QtWidgets.QPushButton("Reset Camera Position")
        self.reset_button.pressed.connect(self.reset_cam_position)
        self.main_vlayout.addWidget(self.reset_button)

        self.renderer = vtk.vtkRenderer()
        vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = vtk_widget.GetRenderWindow().GetInteractor()
        self.window = vtk_widget.GetRenderWindow()

        self.frame.setLayout(self.main_vlayout)
        self.setCentralWidget(self.frame)

        style = MouseInteractorHighLightActor(self)
        style.SetDefaultRenderer(self.renderer)
        self.interactor.SetInteractorStyle(style)

        self.interactor.Initialize()
        self.interactor.Start()
        self.show()

    def setup_mode_slider(self):
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

    def setup_omega_slider(self):
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

    def setup_camera_delta_layout(self):

        self.delta_layout = QtWidgets.QHBoxLayout()

        self.dx_label = QtWidgets.QLabel()
        self.dx_label.setText("Dx: ")
        self.dx_label.setAlignment(QtCore.Qt.AlignLeft)
        self.delta_layout.addWidget(self.dx_label)

        self.dx_box = QtWidgets.QSpinBox()
        self.dx_box.setMinimum(-0x80000000)
        self.dx_box.valueChanged[int].connect(lambda value: self.set_delta_values(value, 0))
        self.delta_layout.addWidget(self.dx_box)

        self.dy_label = QtWidgets.QLabel()
        self.dy_label.setText("Dy: ")
        self.dy_label.setAlignment(QtCore.Qt.AlignLeft)
        self.delta_layout.addWidget(self.dy_label)

        self.dy_box = QtWidgets.QSpinBox()
        self.dy_box.setMinimum(-0x80000000)
        self.dy_box.valueChanged[int].connect(lambda value: self.set_delta_values(value, 1))
        self.delta_layout.addWidget(self.dy_box)

        self.dz_label = QtWidgets.QLabel()
        self.dz_label.setText("Dz: ")
        self.dz_label.setAlignment(QtCore.Qt.AlignLeft)
        self.delta_layout.addWidget(self.dz_label)

        self.dz_box = QtWidgets.QSpinBox()
        self.dz_box.setMinimum(-0x80000000)
        self.dz_box.valueChanged[int].connect(lambda value: self.set_delta_values(value, 2))
        self.delta_layout.addWidget(self.dz_box)

        self.main_vlayout.addLayout(self.delta_layout)

    def set_delta_values(self, value, dx_index):
        global camera_delta_values
        global update_slot
        camera_delta_values[dx_index] = value
        update_slot.set_camera_delta_vals(camera_delta_values)

    def reset_cam_position(self):
        global camera

        #Set default position
        camera.SetPosition(node_count / 2, 30, 30)
        camera.SetFocalPoint(node_count / 2, 0, 0)

    def play_pause_button(self):
        self.is_playing = not self.is_playing
        global timer
        if self.is_playing:
            self.control_button.setText("Pause")
            timer.start(50)
        else:
            self.control_button.setText("Play")
            timer.stop()

    def attach_camera(self):
        global attach_camera_to_node
        global camera_is_attached
        global camera

        attach_camera_to_node = not attach_camera_to_node
        print("Camera Position: ", camera.GetPosition())
        print("Camera Focal Point: ", camera.GetFocalPoint())

        #Remove from node
        if camera_is_attached:
            camera_is_attached = False
            global update_slot

            # Unpin from node
            update_slot.set_camera_pos_actor(None, None)

        if attach_camera_to_node:
            self.attach_camera_button.setText("Remove Camera From Node")
            self.attach_cam_label.setText("Click node to set camera position")
        else:
            self.attach_camera_button.setText("Attach Camera To Node")

    def swap_transparent(self):
        global is_transparent
        is_transparent = not is_transparent

        if is_transparent:
            self.transparent_button.setText("Make Transparent")
        else:
            self.transparent_button.setText("Make Opaque")



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

def reset_camera_position():
    camera.SetPosition(node_count/2, 30, 30)
    camera.SetFocalPoint(node_count/2, 0, 0)

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

    global update_slot
    update_slot = bvtk.vtkUpdate(main_window.window, 0, nodes)
    main_window.add_slot(update_slot)
    # main_window.interactor.AddObserver('TimerEvent', cb.execute)
    # cb.timerId = main_window.interactor.CreateRepeatingTimer(150)
    timer.timeout.connect(update_slot.execute)
    timer.start(50)

    # # Sign up to receive TimerEvent
    reset_camera_position()
    main_window.renderer.SetActiveCamera(camera)

    sys.exit(app.exec_())


if __name__ == "__main__":
    # generate_plot(t_vals, x_vals)
    generate_vtk(t_vals, x_vals)
