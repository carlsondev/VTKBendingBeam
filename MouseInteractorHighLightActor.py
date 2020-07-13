import vtk
import numpy as np
from PyQt5 import QtWidgets
import Settings

class MouseInteractorHighLightActor(vtk.vtkInteractorStyleTrackballCamera):

    def __init__(self, main_window, parent=None):
        self.AddObserver("LeftButtonPressEvent", self.leftButtonPressEvent)
        self.AddObserver("KeyPressEvent", self.key_pressed)
        self.main_window = main_window
        self.LastPickedActor = None
        self.LastPickedProperty = vtk.vtkProperty()

    def key_pressed(self, renderer, event):
        key = self.GetInteractor().GetKeySym()
        azi_step = 2
        ele_step = 2
        if key == "Left":
            Settings.camera.Roll(-azi_step)
        if key == "Right":
            Settings.camera.Roll(azi_step)
        if key == "Up":
            Settings.camera.Elevation(ele_step)
        if key == "Down":
            Settings.camera.Elevation(-ele_step)

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
            self.NewPickedActor.GetProperty().SetColor(0.0, 0.0, 1.0)
            self.NewPickedActor.GetProperty().SetDiffuse(1.0)
            self.NewPickedActor.GetProperty().SetSpecular(0.0)

            if Settings.attach_camera_to_node and not Settings.camera_is_attached:
                Settings.selecting_camera_index += 1
                if Settings.selecting_camera_index == 1:
                    # Adding Position Point
                    Settings.positionActor = self.NewPickedActor
                    Settings.update_slot.set_camera_pos_actor(Settings.positionActor, Settings.camera)
                    self.main_window.attach_cam_label.setText("Click node to set focal point")
                    return

                if Settings.selecting_camera_index == 2:
                    # Adding Focal Point
                    Settings.focalActor = self.NewPickedActor
                    self.main_window.attach_cam_label.setText("")

                pos_center = Settings.positionActor.GetCenter()
                focal_center = Settings.focalActor.GetCenter()
                Settings.selecting_camera_index = 0
                Settings.camera_is_attached = True
                Settings.camera.SetPosition(np.add(pos_center, Settings.camera_delta_values))
                Settings.camera.SetFocalPoint(focal_center)
                Settings.vtk_widget.GetRenderWindow().Render()
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