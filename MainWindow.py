from PyQt5 import QtCore, QtWidgets, QtGui
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from MouseKeyboardInteractor import MouseKeyboardInteractor
import vtk
import Settings


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

        self.frame = QtWidgets.QFrame()

        self.setup_menubar()

        self.main_vlayout = QtWidgets.QVBoxLayout()
        Settings.vtk_widget = QVTKRenderWindowInteractor(self.frame)
        self.main_vlayout.addWidget(Settings.vtk_widget)

        # Setup Sliders
        self.setup_mode_slider()
        self.setup_omega_slider()

        # Setup Play/Pause Button
        self.control_button = QtWidgets.QPushButton("Pause")
        self.control_button.pressed.connect(self.play_pause_button)

        self.main_vlayout.addWidget(self.control_button)

        # Set up attach camera UI
        self.attach_camera_layout = QtWidgets.QHBoxLayout()

        self.attach_camera_button = QtWidgets.QPushButton("Attach Camera To Node")
        self.attach_camera_button.pressed.connect(self.attach_camera)
        self.attach_camera_layout.addWidget(self.attach_camera_button)

        self.attach_cam_label = QtWidgets.QLabel()
        self.attach_cam_label.setText("")
        self.attach_camera_layout.addWidget(self.attach_cam_label)

        self.main_vlayout.addLayout(self.attach_camera_layout)

        # Setup Camera Delta Value Input
        self.setup_camera_delta_layout()

        # Add Camera Position Reset Button
        self.reset_button = QtWidgets.QPushButton("Reset Camera Position")
        self.reset_button.pressed.connect(self.reset_camera_position)
        self.main_vlayout.addWidget(self.reset_button)

        # Setup Window with layout
        self.renderer = vtk.vtkRenderer()
        Settings.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = Settings.vtk_widget.GetRenderWindow().GetInteractor()
        self.window = Settings.vtk_widget.GetRenderWindow()

        self.frame.setLayout(self.main_vlayout)
        self.setCentralWidget(self.frame)

        style = MouseKeyboardInteractor(self)
        style.SetDefaultRenderer(self.renderer)
        self.interactor.SetInteractorStyle(style)

        self.interactor.Initialize()
        self.interactor.Start()
        self.interactor.Render()
        self.show()

    def setup_menubar(self):
        xy_perspective = QtWidgets.QAction("XY", self)
        xy_perspective.setStatusTip("Set XY Perspective")
        xy_perspective.triggered.connect(self.set_xy_perspective)

        yz_perspective = QtWidgets.QAction("YZ", self)
        yz_perspective.setStatusTip("Set YZ Perspective")
        yz_perspective.triggered.connect(self.set_yz_perspective)

        xz_perspective = QtWidgets.QAction("XZ", self)
        xz_perspective.setStatusTip("Set XZ Perspective")
        xz_perspective.triggered.connect(self.set_xz_perspective)

        iso_perspective = QtWidgets.QAction("ISO", self)
        iso_perspective.setStatusTip("Set Iso Perspective")
        iso_perspective.triggered.connect(self.set_iso_perspective)

        self.statusBar()

        main_menu = self.menuBar()
        perspective_menu = main_menu.addMenu('&Perspective')

        perspective_menu.addAction(xy_perspective)
        perspective_menu.addAction(yz_perspective)
        perspective_menu.addAction(xz_perspective)
        perspective_menu.addAction(iso_perspective)

    def set_xy_perspective(self):
        print("XY")
        z_offset = 30
        Settings.camera.SetPosition(Settings.node_count / 2, 0, z_offset)
        Settings.camera.SetFocalPoint(Settings.node_count / 2, 0, 0)
        Settings.camera.SetRoll(0)

    def set_yz_perspective(self):
        print("YZ")
        x_offset = 10
        Settings.camera.SetPosition(Settings.node_count + x_offset, 0, 0)
        Settings.camera.SetFocalPoint(Settings.node_count / 2, 0, 0)
        Settings.camera.SetRoll(0)

    def set_xz_perspective(self):
        print("XZ")
        y_offset = Settings.node_count*2
        Settings.camera.SetPosition(Settings.node_count / 2, y_offset, 0)
        Settings.camera.SetFocalPoint(Settings.node_count / 2, 0, 0)
        Settings.camera.SetRoll(0)

    def set_iso_perspective(self):
        print("ISO")
        x_offset = -20
        z_offset = x_offset
        y_offset = 10
        Settings.camera.SetPosition(x_offset, y_offset, -z_offset)
        Settings.camera.SetFocalPoint(Settings.node_count / 2, 0, 0)
        Settings.camera.SetRoll(0)

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

        normalized_val = (Settings.mode / Settings.mode_max) * 100
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

        minimum_val = -0x80000000

        self.delta_layout = QtWidgets.QHBoxLayout()

        self.dx_label = QtWidgets.QLabel()
        self.dx_label.setText("Dx: ")
        self.dx_label.setAlignment(QtCore.Qt.AlignLeft)
        self.delta_layout.addWidget(self.dx_label)

        self.dx_box = QtWidgets.QSpinBox()
        self.dx_box.setMinimum(minimum_val)
        self.dx_box.valueChanged[int].connect(lambda value: self.set_delta_values(value, 0))
        self.delta_layout.addWidget(self.dx_box)

        self.dy_label = QtWidgets.QLabel()
        self.dy_label.setText("Dy: ")
        self.dy_label.setAlignment(QtCore.Qt.AlignLeft)
        self.delta_layout.addWidget(self.dy_label)

        self.dy_box = QtWidgets.QSpinBox()
        self.dy_box.setMinimum(minimum_val)
        self.dy_box.valueChanged[int].connect(lambda value: self.set_delta_values(value, 1))
        self.delta_layout.addWidget(self.dy_box)

        self.dz_label = QtWidgets.QLabel()
        self.dz_label.setText("Dz: ")
        self.dz_label.setAlignment(QtCore.Qt.AlignLeft)
        self.delta_layout.addWidget(self.dz_label)

        self.dz_box = QtWidgets.QSpinBox()
        self.dz_box.setMinimum(minimum_val)
        self.dz_box.valueChanged[int].connect(lambda value: self.set_delta_values(value, 2))
        self.delta_layout.addWidget(self.dz_box)

        self.main_vlayout.addLayout(self.delta_layout)

    def set_delta_values(self, value, dx_index):

        Settings.camera_delta_values[dx_index] = value
        Settings.update_slot.set_camera_delta_vals(Settings.camera_delta_values)

    def reset_camera_position(self):

        # Set default position
        Settings.camera.SetPosition(Settings.node_count / 2, 30, 30)
        Settings.camera.SetFocalPoint(Settings.node_count / 2, 0, 0)

    def play_pause_button(self):
        self.is_playing = not self.is_playing

        if self.is_playing:
            self.control_button.setText("Pause")
            Settings.timer.start(50)
        else:
            self.control_button.setText("Play")
            Settings.timer.stop()

    def attach_camera(self):

        Settings.attach_camera_to_node = not Settings.attach_camera_to_node
        print("Camera Position: ", Settings.camera.GetPosition())
        print("Camera Focal Point: ", Settings.camera.GetFocalPoint())

        # Remove from node
        if Settings.camera_is_attached:
            Settings.camera_is_attached = False

            # Unpin from node
            Settings.update_slot.set_camera_pos_actor(None, None, None)

        if Settings.attach_camera_to_node:
            self.attach_camera_button.setText("Remove Camera From Node")
            self.attach_cam_label.setText("Click node to set camera position")
        else:
            self.attach_camera_button.setText("Attach Camera To Node")

    def swap_transparent(self):
        Settings.is_transparent = not Settings.is_transparent

        if Settings.is_transparent:
            self.transparent_button.setText("Make Transparent")
        else:
            self.transparent_button.setText("Make Opaque")

    def add_slot(self, vtk_update):
        self.mode_changed_signal.connect(vtk_update.set_mode)
        self.omega_changed_signal.connect(vtk_update.set_omega)

    def mode_value_change(self, value):

        Settings.mode = (value / 100) * Settings.mode_max
        self.mode_changed_signal.emit(Settings.mode)
        print("mode changed: ", Settings.mode)

    def omega_value_change(self, value):

        Settings.omega = value
        self.omega_changed_signal.emit(Settings.omega)
        print("omega changed: ", Settings.omega)