import console_python
from inspect import currentframe

import bpy
import bmesh
from mathutils import Vector

from ase.io.cube import read_cube_data
from skimage.measure import marching_cubes as mc

from .resources.units.units import *
from .preset import Preset
from .camera import Camera
from .animation import Animation


def reset(preset=None, keep_materials=False):
    """
    Resets Blender to an original state. Intended use is at the beginning of a
    script to clean changes made by previous execution of the script.

    Args:
        preset (str | None): The name of a preset to be loaded. Certain Blender
        settings like renderer will be chosen based on this. Default: Currently
        loaded preset.
        keep_materials  (bool): Whether to keep materials defined in Blender.
    """
    remove_cameras()
    remove_meshes()
    remove_collections()
    reset_frame()
    if not keep_materials:
        remove_materials()

    if preset is not None:
        Preset.load(preset)

    reset_blender()


def remove_cameras():
    """
    Removes all excess cameras from the Blender scene.
    """
    for object in bpy.data.objects:
        if object.type == "CAMERA" and object.name != "Camera":
            bpy.data.objects.remove(object)

    Camera.first = True


def reset_frame():
    """
    Resets the frame settings in Blender.
    """
    animation = Animation()
    animation.current_frame = 1
    animation.final_frame = 250
    animation.initial_frame = 1


def set_background_transparent(value):
    """
    Sets the background of the rendered images to be transparent.

    Args:
        value (bool): Whether to make the background transparent.
    """
    bpy.data.scenes["Scene"].render.film_transparent = value


def remove_materials():
    """
    Removes all materials from the Blender scene.
    """
    for material in bpy.data.materials:
        bpy.data.materials.remove(material)


def remove_collections():
    """
    Removes all collections, except the scene collection, from the Blender scene.
    """
    for collection in bpy.data.collections:
        if collection.name != "Collection":
            bpy.data.collections.remove(collection)


def remove_meshes():
    """
    Removes all mesh objects from the Blender scene.
    """
    set_mode("OBJECT")
    bpy.ops.object.select_all(action="DESELECT")

    for object in bpy.context.scene.objects:
        if object.type == "MESH":
            bpy.data.objects.remove(object)

    for mesh in bpy.data.meshes:
        bpy.data.meshes.remove(mesh)


def set_mode(mode):
    """
    Sets the mode of the active object in Blender.

    Args:
        mode (str): The mode to set (e.g., 'OBJECT', 'EDIT', 'SCULPT').
    """
    try:
        bpy.ops.object.mode_set(mode=mode.upper())
    except RuntimeError:
        # Already in mode, do nothing
        pass


def reset_blender():
    """
    Resets the Blender UI settings to their default values.
    """
    set_viewport_engine(Preset.get("blender.viewport_engine"))
    set_viewport_noise(Preset.get("blender.viewport_noise"))
    set_viewport_max_samples(Preset.get("blender.viewport_max_samples"))
    set_viewport_denoise(Preset.get("blender.viewport_denoise"))
    set_wireframe(Preset.get("blender.wireframe"))


def set_viewport_noise(noise):
    """
    Sets the viewport noise level.

    Note:
        This setting is only available in Cycles.

    Args:
        noise (int): The number of samples to use for viewport rendering.
    """
    if bpy.context.scene.render.engine == "CYCLES":
        bpy.data.scenes["Scene"].cycles.preview_adaptive_threshold = noise


def set_viewport_max_samples(samples):
    """
    Sets the maximum number of samples for the viewport.

    Args:
        samples (int): The maximum number of samples to use for viewport rendering.
    """
    if bpy.context.scene.render.engine == "CYCLES":
        bpy.data.scenes["Scene"].cycles.preview_samples = samples
    elif bpy.context.scene.render.engine == "BLENDER_EEVEE":
        bpy.data.scenes["Scene"].eevee.taa_samples = samples


def set_viewport_denoise(denoise):
    """
    Sets the denoising method for the viewport.

    Note:
        This setting is only available in Cycles.

    Args:
        denoise (str): The name of the denoising method to use.
    """
    if bpy.context.scene.render.engine == "CYCLES":
        bpy.data.scenes["Scene"].cycles.use_preview_denoising = denoise


def set_viewport_engine(engine):
    """
    Sets the render engine for the viewport.

    Args:
        engine (str): The name of the render engine to set.
    """
    if engine == "cycles":
        bpy.context.scene.render.engine = "CYCLES"
    elif engine == "eevee":
        bpy.context.scene.render.engine = "BLENDER_EEVEE"
    else:
        raise ValueError(f"Unknown render engine: {engine}")


def set_wireframe(wireframe):
    """
    Sets the wireframe display mode for the viewport.

    Args:
        wireframe (bool): Whether to display objects in wireframe mode.
    """
    for workspace in bpy.data.workspaces:
        for screen in workspace.screens:
            for area in screen.areas:
                if area.type == "VIEW_3D":
                    for space in area.spaces:
                        if space.type == "VIEW_3D":
                            space.overlay.wireframe_opacity = int(wireframe)
                            space.overlay.show_wireframes = True


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


def cut_meshes(x_min=None, x_max=None, y_min=None, y_max=None, z_min=None, z_max=None):
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


def get_viewport_engine():
    """
    Retrieves the current viewport render engine.

    Returns:
        str: The name of the current viewport render engine.
    """
    engine = bpy.context.scene.render.engine
    if engine == "CYCLES":
        return "cycles"
    elif engine == "BLENDER_EEVEE":
        return "eevee"


def set_viewport_engine(engine):
    """
    Sets the render engine for the viewport.

    Args:
        engine (str): The name of the render engine to set.

    Raises:
        ValueError: If the specified engine is not recognized.
    """
    if engine == "cycles":
        bpy.context.scene.render.engine = "CYCLES"
    elif engine == "eevee":
        bpy.context.scene.render.engine = "BLENDER_EEVEE"
    else:
        raise ValueError(f"Unknown render engine: {engine}")
