import math
import vtk
import matplotlib.pyplot as plt
import numpy as np
import beam_vtk as bvtk
from collections import defaultdict

actors = defaultdict(list)

# @ben: here are alternative mode coefficients you can try out:
#       0.59686 , 1.49418,  2.5 , 3.4999
mode = 1.49418
omega = 1.0
x_vals = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
t_vals = np.linspace(0, 2 * math.pi, 20).tolist()


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

    # setup the VTK environment (pipeline objects)
    renderer = vtk.vtkRenderer()
    window = vtk.vtkRenderWindow()

    # bvtk.Node and bvtk.Line are custom objects to make reuse of mappings/actors
    # convenient and less messy.
    nodes = [bvtk.Node() for i in range(N)]

    window.AddRenderer(renderer)
    window.SetSize(800, 800)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    y = beam_deflection(t_vals[10])  # grabbing an arbitrary time to create deflected beam state
    for i in range(N):

        if i < (N - 1):
            #Updates position ahead of time to render next node height
            nodes[i + 1].update_position(x[i + 1], y[i + 1], 0)
            next_node = nodes[i + 1]
        else:
            next_node = nodes[i-1]

        #Generates all node specific actors and adds to renderer
        nodes[i].add_poly_actor_to_renderer(renderer, next_node, x[i], y[i], )

    cb = bvtk.vtkUpdate(renderer, t_vals, 0, nodes)
    interactor.AddObserver('TimerEvent', cb.execute)
    cb.timerId = interactor.CreateRepeatingTimer(500)

    window.Render()

    # # Sign up to receive TimerEvent

    interactor.Start()


if __name__ == "__main__":

    generate_plot(t_vals, x_vals)
    generate_vtk(t_vals, x_vals)
