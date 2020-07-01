import vtk
import beam

class Node(object):
    """
    For rendering the node points as a sphere
    """

    boxDepth = 2
    height = 1

    def __init__(self):

        self.__polyData = vtk.vtkPolyData()
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
        self.__cell = vtk.vtkCellArray()
        self.__data = vtk.vtkPolyData()
        self.__polygon_mapper = vtk.vtkPolyDataMapper()
        self.__polygon_actor = vtk.vtkActor()
        self.__polygon_filter = vtk.vtkTransformPolyDataFilter()
        self.__polygon_transform = vtk.vtkTransform()
        self.__polygon = [vtk.vtkPolygon() for i in range(6)]  # we have 6 sides to each beam box.
        # This is overgeneralized because a beam
        # is really a shell (4 sides) except for
        # end points. But it is valid for now.

    def get_actor(self):  # optional: you can also use setter/getter decorators if you like
        return self.__actor

    def add_actors_to_renderer(self, renderer, next_node, x_val, y_val):
        node_actor = self.get_actor()
        renderer.AddActor(node_actor)

        self.update_position(x_val, y_val, 0)

        back_side_poly = self.get_side_poly_actor(next_node, -1)
        renderer.AddActor(back_side_poly)

        front_side_poly = self.get_side_poly_actor(next_node, 1)
        renderer.AddActor(front_side_poly)

        bottom_poly = self.get_filled_depth_poly(next_node, 0)
        renderer.AddActor(bottom_poly)

        top_poly = self.get_filled_depth_poly(next_node, self.height)
        renderer.AddActor(top_poly)

        side_poly = self.get_back_side_actor()
        renderer.AddActor(side_poly)

    def get_depth_line_actor(self, dy=0):
        line_actor = vtk.vtkActor()

        x = self.__actor.GetCenter()[0]
        y = self.__actor.GetCenter()[1]

        p0 = [x, y+dy, -self.boxDepth]
        p1 = [x, y+dy, self.boxDepth]

        line = vtk.vtkLineSource()
        line.SetPoint1(p0)
        line.SetPoint2(p1)

        # Add the colors we created to the colors array

        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(line.GetOutputPort())

        line_actor.SetMapper(mapper)
        line_actor.GetProperty().SetLineWidth(2)
        line_actor.GetProperty().SetColor(0, 1, 0)

        return line_actor

    def get_side_poly_actor(self, nextNode, zMod):

        if nextNode is None:
            return

        node_center = self.get_actor().GetCenter()
        next_node_center = nextNode.get_actor().GetCenter()

        depth = self.boxDepth * zMod

        points = vtk.vtkPoints()
        points.SetNumberOfPoints(4)
        points.SetPoint(0, node_center[0], node_center[1], depth)
        points.SetPoint(1, next_node_center[0], next_node_center[1], depth)
        points.SetPoint(2, next_node_center[0], next_node_center[1]+self.height, depth)
        points.SetPoint(3, node_center[0], node_center[1]+self.height, depth)

        return self.get_quad_filled_actor(points)

    def get_filled_depth_poly(self, next_node, height):

        if next_node is None:
            return

        node_center = self.get_actor().GetCenter()
        next_node_center = next_node.get_actor().GetCenter()

        points = vtk.vtkPoints()
        points.SetNumberOfPoints(4)
        points.SetPoint(0, node_center[0], height+node_center[1], self.boxDepth)
        points.SetPoint(1, next_node_center[0], height+next_node_center[1], self.boxDepth)
        points.SetPoint(2, next_node_center[0], height+next_node_center[1], -self.boxDepth)
        points.SetPoint(3, node_center[0], height+node_center[1], -self.boxDepth)

        return self.get_quad_filled_actor(points)

    def get_back_side_actor(self):

        node_center = self.get_actor().GetCenter()
        node_x = node_center[0]
        node_y = node_center[1]

        points = vtk.vtkPoints()
        points.SetNumberOfPoints(4)
        points.SetPoint(0,node_x , node_y, self.boxDepth)
        points.SetPoint(1,node_x, node_y+self.height, self.boxDepth)
        points.SetPoint(2,node_x, node_y+self.height, -self.boxDepth)
        points.SetPoint(3,node_x, node_y, -self.boxDepth)

        return self.get_quad_filled_actor(points)

    def get_quad_filled_actor(self, points):
        poly_actor = vtk.vtkActor()

        poly_actor.GetProperty().SetLineWidth(2)
        poly_actor.GetProperty().SetColor(0, 1, 0)

        poly_data = vtk.vtkPolyData()

        # Create the polygon
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(4)  # make a quad
        polygon.GetPointIds().SetId(0, 0)
        polygon.GetPointIds().SetId(1, 1)
        polygon.GetPointIds().SetId(2, 2)
        polygon.GetPointIds().SetId(3, 3)

        lines = vtk.vtkCellArray()
        lines.InsertNextCell(5)
        lines.InsertCellPoint(0)
        lines.InsertCellPoint(1)
        lines.InsertCellPoint(2)
        lines.InsertCellPoint(3)
        lines.InsertCellPoint(0)

        # Add the polygon to a list of polygons

        polygons = vtk.vtkCellArray()
        polygons.InsertNextCell(polygon)

        if beam.transparent:
            poly_data.SetLines(lines)
        else:
            poly_data.SetPolys(polygons)

        poly_data.SetPoints(points)

        poly_mapper = vtk.vtkPolyDataMapper()
        poly_mapper.SetInputData(poly_data)

        poly_actor.SetMapper(poly_mapper)

        return poly_actor

    def update_position(self, x, y, z):
        self.__transform.Identity()
        self.__transform.Translate(x, y, z)

class Line(object):
    """
    For connections between nodes as a line
    """

    def __init__(self):
        # Notice the similiarities with the above:
        # 1) we have a source, a mapper and an actor
        # 2) we also need to connect a mapper to a source
        # 3) an actor is connected to a mapper
        self.__line = vtk.vtkLineSource()
        self.__mapper = vtk.vtkPolyDataMapper()
        self.__actor = vtk.vtkActor()
        self.__mapper.SetInputConnection(self.__line.GetOutputPort())
        self.__actor.SetMapper(self.__mapper)
        self.__actor.GetProperty().SetLineWidth(1)

    def get_actor(self):
        return self.__actor

    def update_position(self, node, point=None):
        if point == 1:
            self.__line.SetPoint1(node.get_actor().GetCenter())
        elif point == 2:
            self.__line.SetPoint2(node.get_actor().GetCenter())
        else:
            raise (ValueError, 'Valid integer values for point is 1 or 2')

class vtkUpdate:
    def __init__(self, renderer,t_vals, x_index, nodes):
        self.renderer = renderer
        self.t_vals = t_vals
        self.x_index = x_index
        self.t_index = 0
        self.nodes = nodes
        self.mod = 1

    def execute(self, obj, event):
        next_node = None
        i = self.x_index
        t = self.t_vals[self.t_index]
        y = beam.beam_deflection(t)

        self.nodes[i].update_position(self.x_index, y[i], 0)

        if i < (len(self.nodes) - 1):
            self.nodes[i + 1].update_position(self.x_index+1, y[i + 1], 0)
            next_node = self.nodes[i + 1]

        if self.t_index >= (len(self.t_vals)-1):
            self.mod = -1
        if self.t_index < 0:
            self.mod = 1
        print(self.t_index)
        self.t_index += self.mod

        iren = obj
        iren.GetRenderWindow().Render()
