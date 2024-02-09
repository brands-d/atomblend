import bpy
from mathutils import Vector

from .material import Material
from .object import Object


class MeshObject(Object):
    """A class representing a mesh object in Blender."""

    def __init__(self):
        super().__init__()
        self.blender_object = bpy.context.active_object

    @property
    def scale(self):
        """The scale of the mesh object."""
        return list(self.blender_object.scale)

    @scale.setter
    def scale(self, scale):
        """Set the scale of the mesh object.

        Args:
            scale (float or list): The scale value(s) to set.
        """
        if isinstance(scale, (int, float)):
            scale = [scale] * 3
        self.blender_object.scale = [s * a for s, a in zip(self.scale, scale)]

    @property
    def material(self):
        """The material of the mesh object."""
        return Material(self.blender_object.active_material.name)

    @material.setter
    def material(self, material):
        """Set the material of the mesh object.

        Args:
            material (Material): The material to set.
        """
        self.blender_object.active_material = material.material
