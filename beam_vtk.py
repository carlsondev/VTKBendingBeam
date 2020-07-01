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
        self.__indices = []
        self.__cell = vtk.vtkCellArray()
        self.__data = vtk.vtkPolyData()
        self.__polygon_mapper = vtk.vtkPolyDataMapper()
        self.__polygon_actor = vtk.vtkActor()
        self.__polygon_filter = vtk.vtkTransformPolyDataFilter()
        self.__polygon_transform = vtk.vtkTransform()
        self.__polygon = [vtk.vtkPolygon() for i in range(1)]  # we have 6 sides to each beam box. But I set this to 1 (a plane)
        # This is overgeneralized because a beam
        # is really a shell (4 sides) except for
        # end points. But it is valid for now.

    #Get node point actor
    def get_actor(self):
        return self.__actor
        
    # Generates all node specific actors and adds to renderer
    def add_actors_to_renderer(self, renderer, next_node):
        node_actor = self.get_actor()
        renderer.AddActor(node_actor)
        renderer.AddActor(self.__polygon_actor)

        # #Create poly actor for back side and add
        # back_side_poly = self.get_side_poly_actor(next_node, -1)
        # renderer.AddActor(back_side_poly)
        # 
        # # Create poly actor for front side and add
        # front_side_poly = self.get_side_poly_actor(next_node, 1)
        # renderer.AddActor(front_side_poly)
        # 
        # # Create poly actor for bottom side and add
        # bottom_poly = self.get_filled_top_depth_poly(next_node, 0)
        # renderer.AddActor(bottom_poly)
        # 
        # # Create poly actor for top side and add
        # top_poly = self.get_filled_top_depth_poly(next_node, self.height)
        # renderer.AddActor(top_poly)
        # 
        # # Create poly actor for side and add
        # side_poly = self.get_side_quad_actor()
        # renderer.AddActor(side_poly)

    # #Get front or back side quad actor
    # def get_side_poly_actor(self, nextNode, zMod):
    # 
    #     if nextNode is None:
    #         return
    # 
    #     node_center = self.get_actor().GetCenter()
    #     next_node_center = nextNode.get_actor().GetCenter()
    # 
    #     depth = self.boxDepth * zMod
    #     #Side quad points
    #     points = vtk.vtkPoints()
    #     points.SetNumberOfPoints(4)
    #     points.SetPoint(0, node_center[0], node_center[1], depth)
    #     points.SetPoint(1, next_node_center[0], next_node_center[1], depth)
    #     points.SetPoint(2, next_node_center[0], next_node_center[1]+self.height, depth)
    #     points.SetPoint(3, node_center[0], node_center[1]+self.height, depth)
    # 
    #     return self.get_quad_filled_actor(points)
    # 
    # #Get quad actor for top
    # def get_filled_top_depth_poly(self, next_node, height):
    # 
    #     if next_node is None:
    #         return
    # 
    #     node_center = self.get_actor().GetCenter()
    #     next_node_center = next_node.get_actor().GetCenter()
    # 
    #     #Top Quad Points
    #     points = vtk.vtkPoints()
    #     points.SetNumberOfPoints(4)
    #     points.SetPoint(0, node_center[0], height+node_center[1], self.boxDepth)
    #     points.SetPoint(1, next_node_center[0], height+next_node_center[1], self.boxDepth)
    #     points.SetPoint(2, next_node_center[0], height+next_node_center[1], -self.boxDepth)
    #     points.SetPoint(3, node_center[0], height+node_center[1], -self.boxDepth)
    # 
    #     return self.get_quad_filled_actor(points)
    # 
    # #Get actor for side quad
    # def get_side_quad_actor(self):
    # 
    #     node_center = self.get_actor().GetCenter()
    #     node_x = node_center[0]
    #     node_y = node_center[1]
    # 
    #     #Side quad points
    #     points = vtk.vtkPoints()
    #     points.SetNumberOfPoints(4)
    #     points.SetPoint(0,node_x , node_y, self.boxDepth)
    #     points.SetPoint(1,node_x, node_y+self.height, self.boxDepth)
    #     points.SetPoint(2,node_x, node_y+self.height, -self.boxDepth)
    #     points.SetPoint(3,node_x, node_y, -self.boxDepth)
    # 
    #     return self.get_quad_filled_actor(points)
    # 
    # #Return quad actor with either wireframe or filled based on "transparent" flag
    # def get_quad_filled_actor(self, points):
    #     poly_actor = vtk.vtkActor()
    # 
    #     poly_actor.GetProperty().SetLineWidth(2)
    #     poly_actor.GetProperty().SetColor(0, 1, 0)
    # 
    #     poly_data = vtk.vtkPolyData()
    # 
    #     # Create the polygon
    #     polygon = vtk.vtkPolygon()
    #     polygon.GetPointIds().SetNumberOfIds(4)  # make a quad
    #     polygon.GetPointIds().SetId(0, 0)
    #     polygon.GetPointIds().SetId(1, 1)
    #     polygon.GetPointIds().SetId(2, 2)
    #     polygon.GetPointIds().SetId(3, 3)
    # 
    #     lines = vtk.vtkCellArray()
    #     lines.InsertNextCell(5)
    #     lines.InsertCellPoint(0)
    #     lines.InsertCellPoint(1)
    #     lines.InsertCellPoint(2)
    #     lines.InsertCellPoint(3)
    #     lines.InsertCellPoint(0)
    # 
    #     polygons = vtk.vtkCellArray()
    #     polygons.InsertNextCell(polygon)
    # 
    #     if beam.transparent:
    #         poly_data.SetLines(lines)
    #     else:
    #         poly_data.SetPolys(polygons)
    # 
    #     poly_data.SetPoints(points)
    # 
    #     poly_mapper = vtk.vtkPolyDataMapper()
    #     poly_mapper.SetInputData(poly_data)
    # 
    #     poly_actor.SetMapper(poly_mapper)
    # 
    #     return poly_actor
    
    def get_polygon_actor(self):
        return None
        
    def set_polygon_point_connections(self, polygon_points):
        self.__indices = polygon_points.index_set

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
        r = self.__polygon_actor.GetCenter()
        self.__polygon_transform.Identity()
        self.__polygon_transform.Translate(x, y-r[1], z)
        self.__polygon_filter.Update()
        for i in range(len(self.__indices)):  
            idx = self.__indices[i]
            point = self.__polygon_filter.GetOutput().GetPoints().GetPoint(idx)
            self.__data.GetPoints().SetPoint(idx, point[0], point[1], point[2])


class PolygonPoints():
    '''
    Object encapsulating the polygon point cloud. This behaves like a container
    '''
    def __init__(self):
        self.__points = vtk.vtkPoints()
        self.__height = 0.0
        self.__width = 1.0
        self.__index_set = []
    
    @property
    def index_set(self):
        return self.__index_set
        
    @property
    def points(self):
        return self.__points
    
    def add_points(self, node1, node2, key=None):
        n = self.__points.GetNumberOfPoints()
        r1 = node1.get_actor().GetCenter() # vilolates Law of Demeter. However, it's a concise description of what is going on
        r2 = node2.get_actor().GetCenter()
        if key == 'last':
            dx = r2[0] - r1[0]
            start_point = r1[0] + dx/2.0
            end_point = r2[0]
        else:
            dx = r2[0] - r1[0]
            start_point = r1[0] - dx/2.0
            end_point = r1[0] + dx/2.0
        self.__points.InsertNextPoint(start_point, self.__height,  self.__width)
        self.__points.InsertNextPoint(start_point, self.__height, -self.__width)
        self.__points.InsertNextPoint(end_point,   self.__height, -self.__width)
        self.__points.InsertNextPoint(end_point,   self.__height,  self.__width)
        self.__index_set = [n, n+1, n+2, n+3]
        
    
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
