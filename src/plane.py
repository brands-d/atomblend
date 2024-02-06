import bpy  # type: ignore
from math import degrees  # type: ignore
from mathutils import Vector, Euler  # type: ignore

from .meshobject import MeshObject
from .material import Material


class Plane(MeshObject):
    def __init__(
        self, size=(100, 100), position=(0, 0, -5), rotation=(0, 0, 0), material=None
    ):
        bpy.ops.mesh.primitive_plane_add(location=position)
        super().__init__()

        if material is not None:
            self.material = Material(material)

        self.size = size

    @property
    def orientation(self):
        return (
            Euler(self.rotation, "XYZ").to_matrix() @ Vector((0, 0, 1))
        ).normalized()

    @orientation.setter
    def orientation(self, orientation):
        self.rotation = [
            degrees(angle)
            for angle in Vector(orientation).to_track_quat("Z", "Y").to_euler()
        ]

    @property
    def size(self):
        return self.scale[:2]

    @size.setter
    def size(self, size):
        self.scale = (size[0], size[1], 1)
