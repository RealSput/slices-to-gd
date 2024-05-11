import json
import bpy
import math
import mathutils

# config start
filename = "" # put JSON output file here
slices = 50 # define how many times to slice mesh here
sel_obj = bpy.context.active_object # currently selected object = mesh to slice
# config end

bpy.ops.object.select_all(action='DESELECT')

lines = []

def get_deepest_y_difference(obj):
    mesh = obj.data
    vertices = [obj.matrix_world @ v.co for v in mesh.vertices]
    deepest_y = min(vertices, key=lambda v: v.y).y
    least_deepest_y = max(vertices, key=lambda v: v.y).y
    difference = least_deepest_y - deepest_y
    return difference, deepest_y, least_deepest_y

for obj in bpy.data.objects:
    if obj.name.startswith("Line"):
        obj.select_set(True)

bpy.ops.object.delete(use_global=False)

diff, dy, ldy = get_deepest_y_difference(sel_obj)
slope = (diff / slices)

tc = 0
y_coordinate = dy

def find_intersection_with_grid(vertex1, vertex2, y_coordinate):
    if vertex1.x == vertex2.x:
        return mathutils.Vector((vertex1.x, y_coordinate, 0))
    if vertex1.y == vertex2.y:
        return None
    m = (vertex2.y - vertex1.y) / (vertex2.x - vertex1.x)
    b = vertex1.y - m * vertex1.x
    x_intersect = (y_coordinate - b) / m
    if min(vertex1.x, vertex2.x) <= x_intersect <= max(vertex1.x, vertex2.x):
        return mathutils.Vector((x_intersect, y_coordinate, 0))
    else:
        return None

def interpolate_height_along_edge(vertex1, vertex2, x_coordinate):
    if vertex2.x == vertex1.x:
        return vertex1.z
    t = (x_coordinate - vertex1.x) / (vertex2.x - vertex1.x)
    z_coordinate = (1 - t) * vertex1.z + t * vertex2.z
    return z_coordinate

def create_line_mesh(vertex1, vertex2):
    center_point = (vertex1 + vertex2) / 2.0
    rotation_angle = -(math.atan2(vertex2.z - vertex1.z, vertex2.x - vertex1.x))
    mesh = bpy.data.meshes.new(name="Line Mesh")
    vertices = [mathutils.Vector((vertex1.x, vertex1.y, 0)), mathutils.Vector((vertex2.x, vertex2.y, 0))]
    edges = [(0, 1)]
    mesh.from_pydata(vertices, edges, [])
    obj = bpy.data.objects.new("Line", mesh)
    bpy.context.collection.objects.link(obj)
    obj.location = center_point
    x_pos = obj.location.x
    y_pos = obj.location.z
    x_scale = vertex2.x - vertex1.x
    rot = math.degrees(rotation_angle)
    obj.rotation_euler = (0, rotation_angle, 0)
    lines.append([x_pos, y_pos, x_scale, rot])
    return obj

full = []

while y_coordinate < ldy:
    y_coordinate += slope
    active_mesh = sel_obj
    if active_mesh and active_mesh.type == 'MESH':
        x_pos = 0
        y_pos = 0
        x_scale = 0
        rot = 0
        for face in active_mesh.data.polygons:
            vertices = [active_mesh.matrix_world @ active_mesh.data.vertices[vertex_index].co for vertex_index in face.vertices]
            min_depth = min(vertices, key=lambda p: p.y).y
            max_depth = max(vertices, key=lambda p: p.y).y
            if min_depth < y_coordinate < max_depth:
                intersections = []
                for i in range(3):
                    intersection = find_intersection_with_grid(vertices[i], vertices[(i + 1) % 3], y_coordinate)
                    if intersection:
                        intersection_with_z = mathutils.Vector((intersection.x, intersection.y, interpolate_height_along_edge(vertices[i], vertices[(i + 1) % 3], intersection.x)))
                        intersections.append(intersection_with_z)
                if len(intersections) >= 2:
                    leftmost_point = min(intersections, key=lambda p: p.x)
                    rightmost_point = max(intersections, key=lambda p: p.x)
                    line_obj = create_line_mesh(leftmost_point, rightmost_point)
                    tc += 1
    else:
        print("No active mesh object found or active object is not a mesh.")
    full.append(lines)
    lines = []

for obj in bpy.data.objects:
    if obj.name.startswith("Line"):
        obj.select_set(True)

bpy.ops.object.origin_set(type='GEOMETRY_ORIGIN', center='MEDIAN')
bpy.ops.object.select_all(action='DESELECT')
        
str = json.dumps(full)
with open(filename, 'w') as f: f.write(str)
