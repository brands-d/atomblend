import bpy
from math import degrees, radians
from mathutils import Euler, Vector


class Object:
    def __init__(self, object=None):
        self._blender_object = object

    @property
    def blender_object(self):
        try:
            self._blender_object.name
        except ReferenceError:
            return None
        except AttributeError:
            return None
        else:
            return self._blender_object

    @blender_object.setter
    def blender_object(self, blender_object):
        self._blender_object = blender_object

    @property
    def location(self):
        return list(self.blender_object.location)

    @location.setter
    def location(self, location):
        self.blender_object.location = Vector(location)

    @property
    def position(self):
        return self.location

    @position.setter
    def position(self, position):
        self.location = Vector(position)

    @property
    def rotation(self):
        return [degrees(angle) for angle in self.blender_object.rotation_euler]

    @rotation.setter
    def rotation(self, rotation):
        self.blender_object.rotation_euler = Euler(
            [radians(angle) for angle in rotation], "XYZ"
        )

    @property
    def name(self):
        return self.blender_object.name

    @name.setter
    def name(self, name):
        self.blender_object.name = name
        for object in bpy.data.objects.values():
            if object.name == name and object.data is not None:
                object.data.name = name

    def make_active(self):
        bpy.ops.object.select_all(action="DESELECT")
        self.blender_object.select_set(True)
        bpy.context.view_layer.objects.active = self.blender_object

    def move(self, translation):
        self.location = Vector(self.blender_object.location) + Vector(translation)

    def rotate(self, rotation, origin="local"):
        if isinstance(origin, str) and origin == "local":
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
            self.rotation = Vector(rotation) + Vector(self.rotation)
        elif isinstance(origin, str) and origin in ("cursor"):
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
            self.rotation = Vector(rotation) + Vector(self.rotation)
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
        else:
            previous_cursor_location = bpy.context.scene.cursor.location.copy()

            if isinstance(origin, str) and origin in ("global", "world", "origin"):
                bpy.context.scene.cursor.location = Vector((0, 0, 0))
            elif isinstance(origin, (tuple, list, Vector)):
                bpy.context.scene.cursor.location = Vector(origin)
            elif isinstance(origin, (Object, bpy.types.Object)):
                bpy.context.scene.cursor.location = Vector(origin.location)

            self.make_active()
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
            self.rotation = Vector(rotation) + Vector(self.rotation)
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
            bpy.context.scene.cursor.location = previous_cursor_location

    def delete(self):
        if self.blender_object is not None:
            bpy.data.objects.remove(self.blender_object, do_unlink=True)
            self._blender_object = None
