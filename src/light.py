import bpy  # type: ignore
from math import radians, degrees

from .object import Object
from .preset import Preset


class Light(Object):
    """
    Represents a light source in the scene.
    """

    first = True

    def __init__(self, energy=None, position=(0, 0, 25), rotation=(0, 0, 0)):
        """
        Initializes a Light object.

        Args:
            energy (float): The energy of the light source. Default: Preset.
            position (tuple): The position of the light source in 3D space. Default is (0, 0, 25).
            rotation (tuple): The rotation of the light source in 3D space. Default is (0, 0, 0).
        """
        if Light.first:
            if "Light" in bpy.data.objects:
                self.blender_object = bpy.data.objects["Light"]
            else:
                for object in bpy.ops.object:
                    if object.type == "LIGHT":
                        self.blender_object = object
                        break

        elif self.blender_object is None:
            bpy.ops.object.light_add(type="SUN")
            self.blender_object = bpy.context.active_object

        self.type = Preset.get("light.default_type").upper()
        self.energy = (
            energy if energy is not None else Preset.get(f"light.{self.type}.energy")
        )
        self.shadows = Preset.get(f"light.{self.type}.shadows")
        if self.type == "sun":
            self.angle = Preset.get("light.sun.angle")
        elif self.type == "point":
            self.radius = Preset.get("light.point.radius")

        self.position = position
        self.rotation = rotation

    @property
    def type(self):
        """
        Get the type of the light source.

        Returns:
            str: The type of the light source.
        """
        return self.blender_object.data.type.lower()

    @type.setter
    def type(self, light_type):
        """
        Set the type of the light source.

        Args:
            light_type (str): The type of the light source.
        """
        self.blender_object.data.type = light_type.upper()

    @property
    def energy(self):
        """
        Get the energy of the light source.

        Returns:
            float: The energy of the light source.
        """
        return self.blender_object.data.energy

    @energy.setter
    def energy(self, energy):
        """
        Set the energy of the light source.

        Args:
            energy (float): The energy of the light source.
        """
        self.blender_object.data.energy = energy

    @property
    def angle(self):
        """
        Get the angle of the light source.

        Note:
            Only works for sun light sources.

        Returns:
            float: The angle of the light source.

        Raises:
            ValueError: If the light source is not a sun light source.
        """
        if self.type != "sun":
            raise ValueError("Angle is only available for sun light sources.")

        return degrees(self.blender_object.data.angle)

    @angle.setter
    def angle(self, angle):
        """
        Set the angle of the light source.

        Note:
            Only works for sun light sources.

        Args:
            angle (float): The angle of the light source.

        Raises:
            ValueError: If the light source is not a sun light source.
        """
        if self.type != "sun":
            raise ValueError("Angle is only available for sun light sources.")

        self.blender_object.data.angle = radians(angle)

    @property
    def radius(self):
        """
        Get the radius of the light source.

        Note:
            Only works for point light sources.

        Returns:
            float: The radius of the light source.

        Raises:
            ValueError: If the light source is not a point light source.
        """
        if self.type != "point":
            raise ValueError("Radius is only available for point light sources.")

        return self.blender_object.data.shadow_soft_size

    @radius.setter
    def radius(self, radius):
        """
        Set the radius of the light source.

        Note:
            Only works for point light sources.

        Args:
            radius (float): The radius of the light source.

        Raises:
            ValueError: If the light source is not a point light source.
        """
        if self.type != "point":
            raise ValueError("Radius is only available for point light sources.")

        self.blender_object.data.shadow_soft_size = radius

    @property
    def shadows(self):
        """
        Whether the light source produces shadows

        Returns:
            bool: Whether the light source produces shadows.
        """
        return self.blender_object.data.use_shadow

    @shadows.setter
    def shadows(self, shadows):
        """
        Set whether the light source produces shadows.

        Args:
            shadows (bool): Whether the light source produces shadows.
        """
        self.blender_object.data.use_shadow = shadows
