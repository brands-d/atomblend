import bpy  # type: ignore
from math import degrees  # type: ignore
from mathutils import Vector, Euler  # type: ignore

from .meshobject import MeshObject
from .material import Material


class Plane(MeshObject):
    def __init__(
        self, size=(100, 100), position=(0, 0, -5), rotation=(0, 0, 0), material=None
    ):
        """
        Initializes a Plane object.

        Args:
            size (tuple, optional): The size of the plane in (width, height) format. Defaults to (100, 100).
            position (tuple, optional): The position of the plane in (x, y, z) format. Defaults to (0, 0, -5).
            rotation (tuple, optional): The rotation of the plane in Euler angles (degrees) format. Defaults to (0, 0, 0).
            material (str, optional): The name of the material to assign to the plane. Defaults to None.
        """
        bpy.ops.mesh.primitive_plane_add(location=position)
        super().__init__()

        if material is not None:
            self.material = Material(material)

        self.size = size

    @property
    def orientation(self):
        """
        Get the orientation vector of the plane.

        Returns:
            mathutils.Vector: The orientation vector of the plane.
        """
        return (
            Euler(self.rotation, "XYZ").to_matrix() @ Vector((0, 0, 1))
        ).normalized()

    @orientation.setter
    def orientation(self, orientation):
        """
        Set the orientation of the plane.

        Args:
            orientation (mathutils.Vector): The new orientation vector of the plane.
        """
        self.rotation = [
            degrees(angle)
            for angle in Vector(orientation).to_track_quat("Z", "Y").to_euler()
        ]

    @property
    def size(self):
        """
        Get the size of the plane.

        Returns:
            tuple: The size of the plane in (width, height) format.
        """
        return self.scale[:2]

    @size.setter
    def size(self, size):
        """
        Set the size of the plane.

        Args:
            size (tuple): The new size of the plane in (width, height) format.
        """
        self.scale = (size[0], size[1], 1)
