import math
import sys
import matplotlib.pyplot as plt
import beam_vtk as bvtk
from collections import defaultdict
from PyQt5 import QtWidgets
from MainWindow import MainWindow
import Settings
from MouseInteractorHighLightActor import MouseInteractorHighLightActor

actors = defaultdict(list)

main = None

class Main:

    @staticmethod
    def get_instance():
        return Main()

    def displacement(self, mode, x):
        beta = math.pi * mode
        r = beta * x
        try:
            k = (math.cos(beta) + math.cosh(beta) / (math.sin(beta) + math.sinh(beta)))
            return (math.cosh(r) - math.cos(r) + k * (math.sin(r) - math.sinh(r)))
        except ZeroDivisionError:
            return 0.0

    def reset_camera_position(self):
        Settings.camera.SetPosition(Settings.node_count/2, 30, 30)
        Settings.camera.SetFocalPoint(Settings.node_count/2, 0, 0)

    def beam_deflection(self, t_val):
        return [self.displacement(Settings.mode, pos / Settings.x_vals[-1]) * math.sin(Settings.omega * t_val) for pos in Settings.x_vals]


    def generate_plot(self, t, x):
        for i, time in enumerate(t):
            y = self.beam_deflection(time)
            plt.figure(1)

            if i == 3:
                plt.plot(x, y, 'bo-')
            else:
                plt.plot(x, y, 'k-', alpha=0.1)

        plt.xlabel('x distance on beam')
        plt.ylabel('y(x,t) displacement')
        plt.grid(True)
        plt.show(block=False)


    def generate_vtk(self, t_vals, x):
        N = len(x)
        N -= 1

        app = QtWidgets.QApplication(sys.argv)
        main_window = MainWindow()

        # bvtk.Node and bvtk.Line are custom objects to make reuse of mappings/actors
        # convenient and less messy.
        nodes = [bvtk.Node() for i in range(N)]

        y = self.beam_deflection(10)  # grabbing an arbitrary time to create deflected beam state
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
        # main_window.interactor.AddObserver('TimerEvent', cb.execute)
        # cb.timerId = main_window.interactor.CreateRepeatingTimer(150)
        Settings.timer.timeout.connect(Settings.update_slot.execute)
        Settings.timer.start(50)

        # # Sign up to receive TimerEvent
        self.reset_camera_position()
        main_window.renderer.SetActiveCamera(Settings.camera)

        sys.exit(app.exec_())

if __name__ == "__main__":
    # generate_plot(t_vals, x_vals)
    main = Main.get_instance()
    main.generate_vtk(Settings.t_vals, Settings.x_vals)
