import bpy  # type: ignore

from .object import Object


class Light(Object):
    first = True

    def __init__(self, energy=10, position=(0, 0, 25), rotation=(0, 0, 0)):
        """
        Initializes a Light object.

        Args:
            energy (float): The energy of the light source. Default is 10.
            position (tuple): The position of the light source in 3D space. Default is (0, 0, 25).
            rotation (tuple): The rotation of the light source in 3D space. Default is (0, 0, 0).
        """
        if Light.first:
            try:
                self.blender_object = bpy.data.objects["Light"]
            except KeyError:
                bpy.ops.object.light_add(type="SUN")
                self.blender_object = bpy.context.active_object
            else:
                self.blender_object.data.type = "SUN"
            finally:
                Light.first = False
        else:
            bpy.ops.object.light_add(type="SUN")
            self.blender_object = bpy.context.active_object

        self.position = position
        self.rotation = rotation
        self.energy = energy

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
