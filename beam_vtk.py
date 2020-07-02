import vtk
import beam
import math


class Node(object):
    """
    For rendering the node points as a sphere
    """

    boxDepth = 2
    height = .5
    num_points_per_poly = 4

    def __init__(self):
        # self.__polyData = vtk.vtkPolyData()
        self.__sphere = vtk.vtkSphereSource()
        self.__mapper = vtk.vtkPolyDataMapper()
        self.__transform = vtk.vtkTransform()
        self.__actor = vtk.vtkActor()
        self.__sphere.SetRadius(.2)
        self.__mapper.SetInputConnection(self.__sphere.GetOutputPort())
        self.__actor.SetUserTransform(self.__transform)
        self.__actor.SetMapper(self.__mapper)
        self.__actor.GetProperty().SetColor(1.0, 0, 0)

        # Attributes for rendering the beam shape. Not implemented,
        # but a good next step
        # @ben: this is a starting place to introduce a beam (or box) around each
        #       sphere object. These objects are not used yet, but I wanted to
        #       attributes needed to create the green polygon shape
        #       This VTK example would be a good place to look at how polygons are
        #       introduced:
        #
        #       https://lorensen.github.io/VTKExamples/site/Python/GeometricObjects/Polygon/
        #
        # @ben: the purpose for defining a polygon object here is to map the object displacement
        #       to a sphere. The polygon objects could also be inside it's own seperate class ...
        self.__indices = []
        self.__cell = vtk.vtkCellArray()
        self.__data = vtk.vtkPolyData()
        self.__polygon_mapper = vtk.vtkPolyDataMapper()
        self.__polygon_actor = vtk.vtkActor()
        self.__polygon_filter = vtk.vtkTransformPolyDataFilter()
        self.__polygon_transform = vtk.vtkTransform()
        self.__points = vtk.vtkPoints()
        self.__polygon = [vtk.vtkPolygon() for i in range(1)]
        # self.__polygons = vtk.vtkCellArray()  # we have 6 sides to each beam box.
        # This is overgeneralized because a beam
        # is really a shell (4 sides) except for
        # end points. But it is valid for now.

    # Get node point actor
    def get_actor(self):
        return self.__actor
        
    def get_poly_actor(self):
        return self.__polygon_actor

    def set_indices(self, idx):
        self.__indices = idx
        
    def set_polygon_point_connections(self, polygon_points):
        # self.__indices = polygon_points.index_set
        # This creates a flat plane
        self.__polygon[0].GetPointIds().SetNumberOfIds(4)
        self.__polygon[0].GetPointIds().SetId(0, self.__indices[0])  # 0 + n
        self.__polygon[0].GetPointIds().SetId(1, self.__indices[1])  # 1 + n
        self.__polygon[0].GetPointIds().SetId(2, self.__indices[2])  # 2 + n
        self.__polygon[0].GetPointIds().SetId(3, self.__indices[3])  # 3 + n
        self.__cell.InsertNextCell(self.__polygon[0])

        self.__data.SetPoints(polygon_points.points)
        self.__data.SetPolys(self.__cell)
        self.__polygon_mapper.SetInputData(self.__data)
        self.__polygon_filter.SetInputData(self.__data)
        self.__polygon_filter.SetTransform(self.__polygon_transform)
        self.__polygon_actor.SetMapper(self.__polygon_mapper)
        self.__polygon_actor.GetProperty().SetColor(0, 1, 0)
        
    def update_position(self, x, y, z):
        self.__transform.Identity()
        self.__transform.Translate(x, y, z)

    def update_polygon_position(self, x, y, z):
        poly_actor_center = self.__polygon_actor.GetCenter()
        # actor_x = poly_actor_center[0]
        # actor_z = poly_actor_center[2]
        self.__polygon_transform.Identity()
        self.__polygon_transform.Translate(x, y-poly_actor_center[1], z)
        self.__polygon_filter.Update()
        for id in self.__indices:
            transformed_point = self.__polygon_filter.GetOutput().GetPoints().GetPoint(id)
            self.__data.GetPoints().SetPoint(id, transformed_point)


class PolygonPoints():
    '''
    Object encapsulating the polygon point cloud. This behaves like a container
    '''
    def __init__(self):
        self.__points = vtk.vtkPoints()
        self.__height = 0.0
        self.__width = 1.0
        
    @property
    def points(self):
        return self.__points
    
    def update_points(self):
        self.__points.GetData().Modified()

    def add_points(self, node1, node2, key=None):
        n = self.__points.GetNumberOfPoints()
        r1 = node1.get_actor().GetCenter() # vilolates Law of Demeter. However, it's a concise description of what is going on
        r2 = node2.get_actor().GetCenter()
        if key == 'first':
            dx = r2[0] - r1[0]
            start_point = r1[0] 
            end_point = r1[0] + dx/2.0
        elif key == 'last':
            dx = r2[0] - r1[0]
            start_point = r1[0] - dx/2.0
            end_point = r2[0] 
        else:
            dx = r2[0] - r1[0]
            start_point = r2[0] - dx/2.0
            end_point = r2[0] + dx/2.0
        self.__points.InsertNextPoint(start_point, self.__height,  self.__width)
        self.__points.InsertNextPoint(start_point, self.__height, -self.__width)
        self.__points.InsertNextPoint(end_point,   self.__height, -self.__width)
        self.__points.InsertNextPoint(end_point,   self.__height,  self.__width)
        return [n, n+1, n+2, n+3]

class vtkUpdate:
    def __init__(self, mode, nodes, polygon_points):
        self.__nodes = nodes
        self.__points = polygon_points
        self.__mode = mode
        self.__timer = 0.0
        self.__omega = 1.0
    
    def execute(self, obj, event):
        for i, node in enumerate(self.__nodes):
            r = node.get_actor().GetCenter()
            deflection = self.__timer/100
            node.update_position(r[0], deflection, r[2])
            node.update_polygon_position(0, deflection, 0)
        self.__points.update_points()
        iren = obj
        iren.GetRenderWindow().Render()
        self.__timer += 10