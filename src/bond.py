import bpy
from mathutils import Vector
from math import acos, atan2, degrees

from .meshobject import MeshObject
from .material import Material
from .preset import Preset


class Bond(MeshObject):
    def __init__(self, atom_1, atom_2):
        """
        Initializes a Bond object between two atoms.

        Args:
            atom_1 (Atom): The first atom connected by the bond.
            atom_2 (Atom): The second atom connected by the bond.
        """
        self.atom_1 = atom_1
        self.atom_2 = atom_2

        bpy.ops.mesh.primitive_cylinder_add()
        super().__init__()

        self.update()
        self.blender_object.scale[:2] = (0.1, 0.1)
        self.material = Material(f'Bond - {Preset.get("material.bonds")}')
        self.name = f"{atom_1.name}-{atom_2.name}"

    @property
    def scale(self):
        """
        Get the scale of the bond.

        Returns:
            list: A list containing the X and Y scale values.
        """
        return list(self.blender_object.scale[:2])

    @scale.setter
    def scale(self, scale):
        """
        Set the scale of the bond.

        Args:
            scale (float or int or list): The scale value(s) to set. If a single value is provided, it will be applied to both X and Y axes.
                If a list of two values is provided, the first value will be applied to the X axis and the second value to the Y axis.
        """
        if isinstance(scale, (int, float)):
            scale = [scale] * 2
        scale = [s * a for s, a in zip(self.scale, scale)]
        self.blender_object.scale = [scale[0], scale[1], self.blender_object.scale[2]]

    def update(self):
        distance = Vector(self.atom_1.position) - Vector(self.atom_2.position)
        location = Vector(self.atom_1.position) - distance / 2

        self.position = location
        self.rotation = (
            0,
            degrees(acos(distance[2] / distance.length)),
            degrees(atan2(distance[1], distance[0])),
        )
        self.blender_object.scale[2] = distance.length / 2
