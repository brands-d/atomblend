import bpy  # type: ignore

from .object import Object


class Light(Object):
    first = True

    def __init__(self, energy=10, position=(0, 0, 25), rotation=(0, 0, 0)):
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
        return self.blender_object.data.energy

    @energy.setter
    def energy(self, energy):
        self.blender_object.data.energy = energy
