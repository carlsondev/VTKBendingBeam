import vtk
import beam
from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)

        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()

    def leftButtonPressEvent(self, obj, event):
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
            self.NewPickedActor.GetProperty().SetColor(1.0, 0.0, 0.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)

            actor_center = self.NewPickedActor.GetCenter()
            actor_x = actor_center[0]
            actor_y = actor_center[1]
            actor_z = actor_center[2]

            if beam.attach_camera_to_node and not beam.camera_is_attached:
                beam.camera_is_attached = True
                d_vals = beam.camera_delta_values
                beam.camera.SetPosition(actor_x,
                                   actor_y,
                                   actor_z)
                beam.camera.SetFocalPoint(actor_x + d_vals[0],
                                          actor_y + d_vals[1],
                                          actor_z + d_vals[2])
                return

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

        self.frame = QtWidgets.QFrame()

        self.main_vlayout = QtWidgets.QVBoxLayout()
        beam.vtk_widget = QVTKRenderWindowInteractor(self.frame)
        self.main_vlayout.addWidget(beam.vtk_widget)

        self.setup_mode_slider()
        self.setup_omega_slider()


        self.control_button = QtWidgets.QPushButton("Pause")
        self.control_button.pressed.connect(self.play_pause_button)

        self.main_vlayout.addWidget(self.control_button)

        self.attach_camera_button = QtWidgets.QPushButton("Attach Camera To Node")
        self.attach_camera_button.pressed.connect(self.attach_camera)

        self.main_vlayout.addWidget(self.attach_camera_button)

        self.setup_camera_delta_layout()

        self.renderer = vtk.vtkRenderer()
        beam.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = beam.vtk_widget.GetRenderWindow().GetInteractor()
        self.window = beam.vtk_widget.GetRenderWindow()

        self.frame.setLayout(self.main_vlayout)
        self.setCentralWidget(self.frame)

        style = MouseInteractorHighLightActor()
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

        normalized_val = (beam.mode / beam.mode_max) * 100
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
        self.dx_box.valueChanged[int].connect(lambda value: self.set_delta_values(value, 0))
        self.delta_layout.addWidget(self.dx_box)

        self.dx_label = QtWidgets.QLabel()
        self.dx_label.setText("Dy: ")
        self.dx_label.setAlignment(QtCore.Qt.AlignLeft)
        self.delta_layout.addWidget(self.dx_label)

        self.dx_box = QtWidgets.QSpinBox()
        self.dx_box.valueChanged[int].connect(lambda value: self.set_delta_values(value, 1))
        self.delta_layout.addWidget(self.dx_box)

        self.dx_label = QtWidgets.QLabel()
        self.dx_label.setText("Dz: ")
        self.dx_label.setAlignment(QtCore.Qt.AlignLeft)
        self.delta_layout.addWidget(self.dx_label)

        self.dx_box = QtWidgets.QSpinBox()
        self.dx_box.valueChanged[int].connect(lambda value: self.set_delta_values(value, 2))
        self.delta_layout.addWidget(self.dx_box)

        self.main_vlayout.addLayout(self.delta_layout)

    def set_delta_values(self, value, dx_index):
        beam.camera_delta_values[dx_index] = value
        print(beam.camera_delta_values)

    def play_pause_button(self):
        self.is_playing = not self.is_playing

        if self.is_playing:
            self.control_button.setText("Pause")
            beam.timer.start(50)
        else:
            self.control_button.setText("Play")
            beam.timer.stop()

    def attach_camera(self):

        beam.attach_camera_to_node = not beam.attach_camera_to_node
        print(beam.camera.GetPosition())

        if beam.attach_camera_to_node:
            self.attach_camera_button.setText("Remove Camera From Node")
        else:
            self.attach_camera_button.setText("Attach Camera To Node")

        beam.camera_is_attached = False
        beam.camera.SetPosition(0, 0, 1)



    def swap_transparent(self):
        beam.is_transparent = not beam.is_transparent

        if beam.is_transparent:
            self.transparent_button.setText("Make Transparent")
        else:
            self.transparent_button.setText("Make Opaque")



    def add_slot(self, vtk_update):
        self.mode_changed_signal.connect(vtk_update.set_mode)
        self.omega_changed_signal.connect(vtk_update.set_omega)

    def mode_value_change(self, value):
        beam.mode = (value / 100) * beam.mode_max
        self.mode_changed_signal.emit(beam.mode)
        print("mode changed: ", beam.mode)

    def omega_value_change(self, value):
        beam.omega = value
        self.omega_changed_signal.emit(beam.omega)
        print("omega changed: ", beam.omega)