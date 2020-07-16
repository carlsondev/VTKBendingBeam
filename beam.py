import math
import sys
import matplotlib.pyplot as plt
import beam_vtk as bvtk
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import Settings


class Main:

    def __init__(self):
        self.__current_function = None
        self.__current_function_params = []

    def set_current_function(self, function, default_params):
        self.__current_function = function
        self.__current_function_params = default_params

    def set_function_param(self, param_index, value):
        try:
            self.__current_function_params[param_index] = value
        except IndexError:
            print("Did not set param: param_index not in param array")
            return
    def eval_current_function(self, x_val, time):
        return self.__current_function(x_val, time, self.__current_function_params)

    def eval_func_for_xvals(self, x_vals, time):
        return_vals = []
        for x in x_vals:
            return_vals.append(self.__current_function(x, time, self.__current_function_params))

        return return_vals


    @staticmethod
    def displacement(mode, x):
        beta = math.pi * mode
        r = beta * x
        try:
            k = (math.cos(beta) + math.cosh(beta) / (math.sin(beta) + math.sinh(beta)))
            displacement = math.cosh(r) - math.cos(r) + k * (math.sin(r) - math.sinh(r))
            return displacement
        except ZeroDivisionError:
            return 0.0

    @staticmethod
    # Params list is [mode, omega]
    def beam_deflection(x_val, time, params):
        return Main.displacement(params[0], x_val / Settings.x_vals[-1]) * math.sin(params[1] * time)

    @staticmethod
    def generate_plot(t, x):
        for i, time in enumerate(t):
            y = Settings.shared_main.eval_func_for_xvals(Settings.x_vals, t)
            plt.figure(1)

            if i == 3:
                plt.plot(x, y, 'bo-')
            else:
                plt.plot(x, y, 'k-', alpha=0.1)

        plt.xlabel('x distance on beam')
        plt.ylabel('y(x,t) displacement')
        plt.grid(True)
        plt.show(block=False)

    @staticmethod
    def get_active_camera(ren_window):
        ren_window.GetRenderers().GetFirstRenderer().GetActiveCamera()

    @staticmethod
    def generate_vtk(t_vals, x):
        N = len(x)
        N -= 1

        app = QtWidgets.QApplication(sys.argv)
        main_window = MainWindow()
        Settings.shared_main.set_current_function(Main.beam_deflection, [Settings.mode, Settings.omega])

        # bvtk.Node and bvtk.Line are custom objects to make reuse of mappings/actors
        # convenient and less messy.
        nodes = [bvtk.Node() for i in range(N)]

        y = Settings.shared_main.eval_func_for_xvals(Settings.x_vals, 10) # grabbing an arbitrary time to create deflected beam state
        for i in range(N):

            if i < (N - 1):
                # Updates position ahead of time to render next node height
                nodes[i + 1].update_position(x[i + 1], y[i + 1], 0)
                next_node = nodes[i + 1]
            else:
                next_node = nodes[i - 1]

            # Generates all node specific actors and adds to renderer
            nodes[i].add_poly_actor_to_renderer(main_window.renderer, next_node, x[i], y[i])

        main_window.ren_window.Render()

        Settings.update_slot = bvtk.vtkUpdate(main_window, 0, nodes)
        main_window.add_slot(Settings.update_slot)

        Settings.timer.timeout.connect(Settings.update_slot.execute)
        Settings.timer.start(50)

        # Sign up to receive TimerEvent
        main_window.reset_camera_position()
        #main_window.renderer.SetActiveCamera(Settings.camera)

        sys.exit(app.exec_())

if __name__ == "__main__":
    # generate_plot(t_vals, x_vals)

    Main.generate_vtk(Settings.t_vals, Settings.x_vals)
