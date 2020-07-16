from PyQt5 import QtCore
from collections import defaultdict
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import numpy as np
import vtk
import math
from beam import Main
from MainWindow import MainWindow

actors = defaultdict(list)

# @ben: here are alternative mode coefficients you can try out:
#       0.6 , 1.5,  2.5 , 3.5
node_count = 21
nodes = []
x_vals = range(node_count)
t_val_step = (2 * math.pi) / 40
current_t_val = 0

mode = 2.5
mode_max = 3.5
omega = 1
is_playing = True

attach_camera_to_node = False
camera_is_attached = False
camera_delta_values = [0, 0, 0]

# Index = 0: Not selecting, 1: Selecting Position, 2: Selecting Focal Point
selecting_camera_index = 0
focalActor: vtk.vtkActor
positionActor: vtk.vtkActor

timer = QtCore.QTimer()

vtk_widget: QVTKRenderWindowInteractor

update_slot = None
shared_main = Main()
main_window = None