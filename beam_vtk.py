import vtk
import beam
import math


class Node(object):
    """
    For rendering the node points as a sphere
    """

    boxDepth = 2
    height = 1
    num_points_per_poly = 4



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
        self.__actor.GetProperty().SetColor(0, 0, 1)

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
        self.__points = vtk.vtkPoints()
        self.__polygons = vtk.vtkCellArray()  # we have 6 sides to each beam box.
        self.__indices = []
        self.__lines = vtk.vtkCellArray()
        # This is overgeneralized because a beam
        # is really a shell (4 sides) except for
        # end points. But it is valid for now.

    # Get node point actor
    def get_actor(self):
        return self.__actor

    # Generates all node specific actors and adds to renderer
    def add_poly_actor_to_renderer(self, renderer, next_node, x_val, y_val):
        node_actor = self.get_actor()
        renderer.AddActor(node_actor)

        self.update_position(x_val, y_val, 0)

        # Add back side quad data
        self.get_fb_quad_points(next_node, -1)

        # Add front side quad data
        self.get_fb_quad_points(next_node, 1)

        # Add bottom side quad data
        self.get_top_quad_points(next_node, -self.height)

        # Add top side quad data
        self.get_top_quad_points(next_node, self.height)

        # Add left side quad data
        self.add_lr_side_quad_data(next_node, -1)

        # Add right side quad data
        self.add_lr_side_quad_data(next_node, 1)

        # Update nodes polyData
        self.__polyData.SetLines(self.__lines)
        if not beam.is_transparent:
            self.__polyData.SetPolys(self.__polygons)
        self.__polyData.SetPoints(self.__points)

        # Set Transformation/Filter/Mapper properties
        self.__polygon_mapper.SetInputData(self.__polyData)
        self.__polygon_filter.SetInputData(self.__polyData)

        self.__polygon_filter.SetTransform(self.__polygon_transform)
        self.__polygon_actor.SetMapper(self.__polygon_mapper)
        self.__polygon_actor.GetProperty().SetLineWidth(2)
        self.__polygon_actor.GetProperty().SetColor(0, 1, 0)

        renderer.AddActor(self.__polygon_actor)

    # Add front or back side quad data
    def get_fb_quad_points(self, nextNode, zMod):

        node_center = self.get_actor().GetCenter()
        node_x = node_center[0]
        node_y = node_center[1]

        #Non rendered last point
        next_node_x = beam.x_vals[-1]
        next_node_y = beam.beam_deflection(beam.current_t_val)[next_node_x]

        if nextNode is not None:
            next_node_x = nextNode.get_actor().GetCenter()[0]
            next_node_y = nextNode.get_actor().GetCenter()[1]

        dx = math.fabs(next_node_x - node_x) / 2

        depth = self.boxDepth * zMod
        # Side quad points
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(4)

        points.SetPoint(0, node_x - dx, node_y - self.height, depth)
        points.SetPoint(1, node_x + dx, next_node_y - self.height, depth)
        points.SetPoint(2, node_x + dx, next_node_y + self.height, depth)
        points.SetPoint(3, node_x - dx, node_y + self.height, depth)

        self.add_quad_data(points)

    # Add top quad data
    def get_top_quad_points(self, next_node, height, last=False):

        node_center = self.get_actor().GetCenter()

        node_x = node_center[0]
        node_y = node_center[1]

        next_node_x = beam.x_vals[-1]
        next_node_y = beam.beam_deflection(beam.current_t_val)[next_node_x]

        if next_node is not None:
            next_node_center = next_node.get_actor().GetCenter()
            next_node_x = next_node_center[0]
            next_node_y = next_node_center[1]

        dx = math.fabs(next_node_x - node_x) / 2

        # Top Quad Points
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(4)

        if last:
            height *=-1

        points.SetPoint(0, node_x - dx, node_y + height, self.boxDepth)
        points.SetPoint(1, node_x + dx, next_node_y + height, self.boxDepth)
        points.SetPoint(2, node_x + dx, next_node_y + height, -self.boxDepth)
        points.SetPoint(3, node_x - dx, node_y + height, -self.boxDepth)

        self.add_quad_data(points)


    # Get actor for left or right side quad
    def add_lr_side_quad_data(self, next_node, dx_mod):

        node_center = self.get_actor().GetCenter()
        node_x = node_center[0]
        node_y = node_center[1]

        next_node_x = beam.x_vals[-1]
        next_node_y = beam.beam_deflection(beam.current_t_val)[next_node_x]

        if next_node is not None:
            next_node_center = next_node.get_actor().GetCenter()
            next_node_x = next_node_center[0]
            next_node_y = next_node_center[1]

        dx = math.fabs((next_node_x - node_x) / 2) * dx_mod

        # Side quad points
        points = vtk.vtkPoints()
        points.SetNumberOfPoints(4)

        if dx_mod > 0:
            points.SetPoint(0, node_x + dx, next_node_y - self.height, self.boxDepth)
            points.SetPoint(1, node_x + dx, next_node_y + self.height, self.boxDepth)
            points.SetPoint(2, node_x + dx, next_node_y + self.height, -self.boxDepth)
            points.SetPoint(3, node_x + dx, next_node_y - self.height, -self.boxDepth)
        else:
            points.SetPoint(0, node_x + dx, node_y - self.height, self.boxDepth)
            points.SetPoint(1, node_x + dx, node_y + self.height, self.boxDepth)
            points.SetPoint(2, node_x + dx, node_y + self.height, -self.boxDepth)
            points.SetPoint(3, node_x + dx, node_y - self.height, -self.boxDepth)

        self.add_quad_data(points)

    # Return quad actor with either wireframe or filled based on "transparent" flag
    def add_quad_data(self, points):

        # Each point index is ((the index of its poly) * (num points in poly)) + (relative id of point)
        poly_index = self.__polygons.GetNumberOfCells()

        id_base = poly_index * self.num_points_per_poly

        # Generates ID Lists for adding quad points
        point_id_list = vtk.vtkIdList()
        rel_id_list = vtk.vtkIdList()
        for rel_id in range(self.num_points_per_poly):
            rel_id_list.InsertNextId(rel_id)
            index = id_base + rel_id
            self.__indices.append(index)
            point_id_list.InsertNextId(index)

        # Insert quad points to node points
        self.__points.InsertPoints(point_id_list, rel_id_list, points)

        # Create the polygon
        polygon = vtk.vtkPolygon()
        polygon.GetPointIds().SetNumberOfIds(self.num_points_per_poly)  # make a quad
        polygon.GetPointIds().SetId(0, id_base + 0)
        polygon.GetPointIds().SetId(1, id_base + 1)
        polygon.GetPointIds().SetId(2, id_base + 2)
        polygon.GetPointIds().SetId(3, id_base + 3)

        self.__lines.InsertNextCell(self.num_points_per_poly + 1)
        self.__lines.InsertCellPoint(id_base + 0)
        self.__lines.InsertCellPoint(id_base + 1)
        self.__lines.InsertCellPoint(id_base + 2)
        self.__lines.InsertCellPoint(id_base + 3)
        self.__lines.InsertCellPoint(id_base + 0)

        self.__polygons.InsertNextCell(polygon)

    def update_position(self, x, y, z):
        self.__transform.Identity()
        self.__transform.Translate(x, y, z)

    def update_polygon_position(self, y, next_node):

        self.__lines.Reset()
        self.__polygons.Reset()
        self.__points.Reset()

        # Add back side quad data
        self.get_fb_quad_points(next_node, -1)

        # Add front side quad data
        self.get_fb_quad_points(next_node, 1)

        # Add bottom side quad data
        self.get_top_quad_points(next_node, -self.height)

        # Add top side quad data
        self.get_top_quad_points(next_node, self.height)

        # Add left side quad data
        self.add_lr_side_quad_data(next_node, -1)

        # Add right side quad data
        self.add_lr_side_quad_data(next_node, 1)

        # Update nodes polyData
        self.__polyData.SetLines(self.__lines)
        self.__polyData.SetPolys(self.__polygons)

        self.__polyData.SetPoints(self.__points)


        # for id in self.__indices:
        #     transformed_point = self.__polygon_filter.GetOutput().GetPoints().GetPoint(id)
        #     self.__polyData.GetPoints().SetPoint(id, transformed_point)
        #     self.__points.GetData().Modified()


class vtkUpdate:
    def __init__(self, render_window, x_index, nodes):
        self.x_index = x_index
        self.nodes = nodes
        self.ren_window = render_window

    def set_mode(self, val):
        beam.mode = val

    def set_omega(self, val):
        beam.omega = val

    def execute(self):

        i = self.x_index
        y = beam.beam_deflection(beam.current_t_val)


        for i in range(len(self.nodes)):
            node = self.nodes[i]

            next_node = None

            if i < (len(self.nodes) - 1):
                self.nodes[i + 1].update_position(i + 1, y[i + 1], 0)
                next_node = self.nodes[i + 1]

            node.update_position(i, y[i], 0)
            node.update_polygon_position(y[i], next_node)


        beam.current_t_val+=beam.t_val_step
        #print("Current Time: ", beam.current_t_val)

        self.ren_window.Render()
