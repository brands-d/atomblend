import bpy
from mathutils import Vector
from math import acos, atan2, degrees

from .meshobject import MeshObject
from .material import Material
from .preset import Preset


class Bond(MeshObject):
    def __init__(self, atom_1, atom_2):
        self.atom_1 = atom_1
        self.atom_2 = atom_2
        distance = Vector(atom_1.position) - Vector(atom_2.position)
        location = Vector(atom_1.position) - distance / 2

        bpy.ops.mesh.primitive_cylinder_add(location=location)
        super().__init__()

        self.position = location
        self.rotation = (
            0,
            degrees(acos(distance[2] / distance.length)),
            degrees(atan2(distance[1], distance[0])),
        )
        self.blender_object.scale = (0.1, 0.1, distance.length / 2)
        self.material = Material(f'Bond - {Preset.get("material.bonds")}')
        self.name = f"{atom_1.name}-{atom_2.name}"

    @property
    def scale(self):
        return list(self.blender_object.scale[:2])

    @scale.setter
    def scale(self, scale):
        if isinstance(scale, (int, float)):
            scale = [scale] * 2
        scale = [s * a for s, a in zip(self.scale, scale)]
        self.blender_object.scale = [scale[0], scale[1], self.blender_object.scale[2]]
