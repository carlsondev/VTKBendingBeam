import math
import sys
import matplotlib.pyplot as plt
import beam_vtk as bvtk
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import Settings


class Main:

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
    def beam_deflection(t_val):
        return [Main.displacement(Settings.mode, pos / Settings.x_vals[-1]) * math.sin(Settings.omega * t_val) for pos in Settings.x_vals]

    @staticmethod
    def generate_plot(t, x):
        for i, time in enumerate(t):
            y = Main.beam_deflection(time)
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
    def generate_vtk(t_vals, x):
        N = len(x)
        N -= 1

        app = QtWidgets.QApplication(sys.argv)
        main_window = MainWindow()

        # bvtk.Node and bvtk.Line are custom objects to make reuse of mappings/actors
        # convenient and less messy.
        nodes = [bvtk.Node() for i in range(N)]

        y = Main.beam_deflection(10)  # grabbing an arbitrary time to create deflected beam state
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

        Settings.update_slot = bvtk.vtkUpdate(main_window.window, 0, nodes)
        main_window.add_slot(Settings.update_slot)

        Settings.timer.timeout.connect(Settings.update_slot.execute)
        Settings.timer.start(50)

        # Sign up to receive TimerEvent
        main_window.reset_camera_position()
        main_window.renderer.SetActiveCamera(Settings.camera)

        sys.exit(app.exec_())


if __name__ == "__main__":
    # generate_plot(t_vals, x_vals)

    Main.generate_vtk(Settings.t_vals, Settings.x_vals)
