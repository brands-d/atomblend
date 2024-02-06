import bpy
from mathutils import Vector

from .material import Material
from .object import Object


class MeshObject(Object):
    def __init__(self):
        super().__init__()
        self.blender_object = bpy.context.active_object

    @property
    def scale(self):
        return list(self.blender_object.scale)

    @scale.setter
    def scale(self, scale):
        if isinstance(scale, (int, float)):
            scale = [scale] * 3
        self.blender_object.scale = [s * a for s, a in zip(self.scale, scale)]

    @property
    def material(self):
        return Material(self.blender_object.active_material.name)

    @material.setter
    def material(self, material):
        self.blender_object.active_material = material.material
