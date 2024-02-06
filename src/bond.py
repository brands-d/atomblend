import bpy
from mathutils import Vector
from math import acos, atan2, degrees

from .meshobject import MeshObject


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
        self.scale = (0.1, 0.1, distance.length / 2)

        self.name = f"{atom_1.name}-{atom_2.name}"
