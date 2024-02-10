import bmesh
import bpy
import console_python
from ase.io.cube import read_cube_data
from mathutils import Vector
from skimage.measure import marching_cubes as mc
from inspect import currentframe

BOHR = 0.529177
ANGSTROM = 1


def reset():
    """
    Resets the Blender scene by removing all objects, meshes, and collections.
    """
    try:
        bpy.ops.object.mode_set(mode="OBJECT")
    except:
        pass
    bpy.ops.object.select_all(action="DESELECT")

    for object in bpy.context.scene.objects:
        if object.type == "MESH":
            bpy.data.objects.remove(object)

    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)

    for collection in bpy.data.collections:
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)


def render(filepath=None, show=True, mode="quality"):
    """
    Renders the current scene using the specified rendering mode and saves the image to a file.

    Parameters:
    - filepath (str): The path to save the rendered image. If None, the image will not be saved.
    - show (bool): Whether to display the rendered image in a separate window.
    - mode (str): The rendering mode to use. Options are "fast", "performance", "eevee" for fast rendering,
    and "slow", "quality", "beautiful", "cycles" for high-quality rendering.
    """
    original_display_type = bpy.context.preferences.view.render_display_type
    if show:
        bpy.context.preferences.view.render_display_type = "WINDOW"

    engine = bpy.context.scene.render.engine
    if mode.lower() in ["fast", "performance", "eevee"]:
        bpy.context.scene.render.engine = "BLENDER_EEVEE"
    elif mode.lower() in ["slow", "quality", "beautiful", "cycles"]:
        bpy.context.scene.render.engine = "CYCLES"

    if filepath is not None:
        bpy.context.scene.render.filepath = str(filepath)
        if show:
            bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)
        else:
            bpy.ops.render.render(write_still=True)
    else:
        if show:
            bpy.ops.render.render("INVOKE_DEFAULT")
        else:
            bpy.ops.render.render()

    bpy.context.scene.render.engine = engine
    bpy.context.preferences.view.render_display_type = original_display_type


def marching_cubes_VASP(density, unit_cell, name, level=None):
    """
    Generates a mesh using the marching cubes algorithm from VASP density data.

    Parameters:
    - density (ndarray): The density data.
    - unit_cell (tuple): The unit cell dimensions.
    - name (str): The name of the mesh object.
    - level (float): The isosurface level. If None, the default level will be used.

    Returns:
    - object: The generated mesh object.
    """
    vertices, faces, *_ = mc(density, level=level)
    vertices = [
        _vertex_transform(vertex, unit_cell, density.shape) for vertex in vertices
    ]
    edges = [[face[i], face[(i + 1) % 3]] for face in faces for i in range(3)]

    mesh = bpy.data.meshes.new(name=name)
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()
    return bpy.data.objects.new(name, mesh)


def marching_cubes_gaussian(density, origin, axes, name, level=None):
    """
    Generates a mesh using the marching cubes algorithm from Gaussian density data.

    Parameters:
    - density (ndarray): The density data.
    - origin (Vector): The origin of the density data.
    - axes (tuple): The axes vectors of the density data.
    - name (str): The name of the mesh object.
    - level (float): The isosurface level. If None, the default level will be used.

    Returns:
    - object: The generated mesh object.
    """
    vertices, faces, *_ = mc(density, level=level)
    vertices = [
        [Vector(vertex).dot(Vector(axes[i])) + origin[i] for i in range(3)]
        for vertex in vertices
    ]
    edges = [[face[i], face[(i + 1) % 3]] for face in faces for i in range(3)]

    mesh = bpy.data.meshes.new(name=name)
    mesh.from_pydata(vertices, edges, faces)
    mesh.update()
    return bpy.data.objects.new(name, mesh)


def _vertex_transform(vertex, unit_cell, shape):
    """
    Transforms a vertex coordinate based on the unit cell dimensions and shape of the density data.

    Parameters:
    - vertex (tuple): The vertex coordinate.
    - unit_cell (tuple): The unit cell dimensions.
    - shape (tuple): The shape of the density data.

    Returns:
    - tuple: The transformed vertex coordinate.
    """
    new = (vertex[0] - 1) * unit_cell[0] / shape[0]
    new += (vertex[1] - 1) * unit_cell[1] / shape[1]
    new += (vertex[2] - 1) * unit_cell[2] / shape[2]
    return new


def flip_normals(object):
    """
    Flips the normals of a mesh object.

    Parameters:
    - object (object): The mesh object to flip the normals of.
    """
    bpy.context.view_layer.objects.active = object
    bpy.ops.object.mode_set(mode="OBJECT")
    object = bpy.context.active_object

    if object.type == "MESH":
        mesh = object.data
        for polygon in mesh.polygons:
            polygon.flip()

        mesh.update()

        bpy.ops.object.mode_set(mode="EDIT")
        bpy.ops.mesh.normals_make_consistent(inside=False)
        bpy.ops.object.mode_set(mode="OBJECT")


def read_cube(filename):
    """
    Reads a Gaussian cube file and returns the density data, origin, axes, and unit cell.

    Parameters:
    - filename (str): The path to the cube file.

    Returns:
    - tuple: The density data, origin, axes, and unit cell.
    """
    with open(filename, "r") as file:
        lines = file.readlines()

    aux = [None, None, None, None]
    for i in range(0, 4):
        units, *axis = lines[i + 2].split()
        units = ANGSTROM if float(units) < 0 else BOHR
        aux[i] = Vector([float(i) * units for i in axis])

    origin, x, y, z = aux
    data, atoms = read_cube_data(filename)

    return data, origin, (x, y, z), atoms.cell


def remove_mesh(x_min=None, x_max=None, y_min=None, y_max=None, z_min=None, z_max=None):
    """
    Removes mesh objects within the specified coordinate range.

    Parameters:
    - x_min (float): The minimum x-coordinate.
    - x_max (float): The maximum x-coordinate.
    - y_min (float): The minimum y-coordinate.
    - y_max (float): The maximum y-coordinate.
    - z_min (float): The minimum z-coordinate.
    - z_max (float): The maximum z-coordinate.
    """
    for object in bpy.context.scene.objects:
        if object.type != "MESH":
            continue

        bpy.context.view_layer.objects.active = object
        object.select_set(True)
        bpy.ops.object.mode_set(mode="EDIT")

        mesh = bmesh.from_edit_mesh(object.data)
        mesh.faces.ensure_lookup_table()
        mesh.edges.ensure_lookup_table()
        mesh.verts.ensure_lookup_table()
        verts_to_delete = []
        for v in mesh.verts:
            co = object.matrix_world @ v.co
            if (
                (x_min is not None and co.x > x_min)
                or (x_max is not None and co.x < x_max)
                or (y_min is not None and co.y > y_min)
                or (y_max is not None and co.y < y_max)
                or (z_min is not None and co.z > z_min)
                or (z_max is not None and co.z < z_max)
            ):
                verts_to_delete.append(v)
        bmesh.ops.delete(mesh, geom=verts_to_delete, context="VERTS")
        bmesh.update_edit_mesh(object.data)
        bpy.ops.object.mode_set(mode="OBJECT")

        object.select_set(False)


def get_console():
    """
    Retrieves the Blender Python console.

    Returns:
    - object: The Blender Python console object.
    """
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == "CONSOLE":
                for region in area.regions:
                    if region.type == "WINDOW":
                        console = console_python.get_console(hash(region))
                        if console:
                            return console[0]


def interactive():
    """
    Enables interactive mode by updating the console locals with the current frame's locals.
    """
    frame = currentframe()
    try:
        console = get_console()
        console.locals.update(frame.f_back.f_locals)
    finally:
        del frame


def set_frame(frame):
    """
    Sets the frame of the Blender scene.

    Parameters:
    - frame (int): The frame number to set.
    """
    bpy.context.scene.frame_set(frame)


def get_frame():
    """
    Gets the frame of the Blender scene.

    Returns:
    - int: The current frame number.
    """
    return bpy.context.scene.frame_current


def set_frame_range(start, end):
    """
    Sets the frame range of the Blender scene.

    Parameters:
    - start (int): The start frame number.
    - end (int): The end frame number.
    """
    bpy.context.scene.frame_start = start
    bpy.context.scene.frame_end = end


def get_frame_range():
    """
    Gets the frame range of the Blender scene.

    Returns:
    - tuple: The start and end frame numbers.
    """
    return bpy.context.scene.frame_start, bpy.context.scene.frame_end
