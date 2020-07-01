import vtk
import random

import sys

sys.path.append("./modules")

R = 2
botx = -2
topx = 2
topz = 2

class vtkTimerCallback():
    def __init__(self):
        self.timer_count = 0
        self.actors = []

    def execute(self, obj, event):
        iren = obj
        wren = iren.GetRenderWindow()
        renderer = wren.GetRenderers().GetFirstRenderer()

        # print self.timer_count
        x, y, z = self.actors[0].GetCenter()

        if ((z - R) > botx):
            z = z - R

            print
            x, y, z

            renderer.RemoveActor(self.actors[0])
            self.actors.pop()

            sphereSource = vtk.vtkSphereSource()
            sphereSource.SetCenter(x, y, z)
            sphereSource.SetRadius(R)

            # Create a mapper and actor
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(sphereSource.GetOutputPort())
            self.actors.append(vtk.vtkActor())
            self.actors[0].SetMapper(mapper)

            renderer.AddActor(self.actors[0])
        else:
            print
            len(self.actors)

            if (len(self.actors) == 1):
                cx = x
                cy = y
                cz = topz - R

                sphereSource = vtk.vtkSphereSource()
                sphereSource.SetCenter(cx, cy, cz)
                sphereSource.SetRadius(R)

                # Create a mapper and actor
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(sphereSource.GetOutputPort())
                self.actors.append(vtk.vtkActor())
                self.actors[1].SetMapper(mapper)

                renderer.AddActor(self.actors[1])
            elif (len(self.actors) == 2):
                x, y, z = self.actors[1].GetCenter()

                renderer.RemoveActor(self.actors[1])
                self.actors.pop()

                z = z - R

                sphereSource = vtk.vtkSphereSource()
                sphereSource.SetCenter(x, y, z)
                sphereSource.SetRadius(R)

                # Create a mapper and actor
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputConnection(sphereSource.GetOutputPort())
                self.actors.append(vtk.vtkActor())
                self.actors[1].SetMapper(mapper)

                renderer.AddActor(self.actors[1])

        iren.GetRenderWindow().Render()
        self.timer_count += 1


def main():
    # Create a sphere
    sphereSource = vtk.vtkSphereSource()

    cx = random.uniform(botx + R, topx - R)
    cy = random.uniform(boty + R, topy - R)
    cz = topz - R

    sphereSource.SetCenter(cx, cy, cz)
    sphereSource.SetRadius(R)

    # Setup a renderer, render window, and interactor
    renderer = vtk.vtkRenderer()
    renderWindow = vtk.vtkRenderWindow()
    # renderWindow.SetWindowName("Test")

    renderWindow.AddRenderer(renderer);
    renderWindowInteractor = vtk.vtkRenderWindowInteractor()
    renderWindowInteractor.SetRenderWindow(renderWindow)

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(sphereSource.GetOutputPort())
    sactor = vtk.vtkActor()
    sactor.SetMapper(mapper)
    renderer.AddActor(sactor)

    # add cube
    sources = []

    addcube_to_source(sources, botx, boty, botz, \
                      topx, topy, topz)

    for s in sources:
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(s.GetOutputPort())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        renderer.AddActor(actor)

    # Render and interact
    renderWindow.Render()

    # Initialize must be called prior to creating timer events.
    renderWindowInteractor.Initialize()

    # Sign up to receive TimerEvent
    cb = vtkTimerCallback()
    cb.actors.append(sactor)
    renderWindowInteractor.AddObserver('TimerEvent', cb.execute)
    timerId = renderWindowInteractor.CreateRepeatingTimer(100);

    # start the interaction and timer
    renderWindowInteractor.Start()


if __name__ == '__main__':
    main()