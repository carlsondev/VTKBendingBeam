import vtk
import random

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
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)

    # create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # create cube
    cube = vtk.vtkCubeSource()

    # mapper
    cubeMapper = vtk.vtkPolyDataMapper()
    cubeMapper.SetInput(cube.GetOutput())

    # actor
    cubeActor = vtk.vtkActor()
    cubeActor.SetMapper(cubeMapper)

    # assign actor to the renderer
    ren.AddActor(cubeActor)

    # enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start()


if __name__ == '__main__':
    main()