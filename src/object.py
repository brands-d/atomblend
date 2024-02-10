import bpy
from math import degrees, radians
from mathutils import Euler, Vector

from .lib import get_frame, set_frame


class Object:
    """
    A class representing an object in Blender.

    Attributes:
        blender_object (bpy.types.Object): The Blender object associated with this Object instance.

    Methods:
        make_active(): Makes the object active in the scene.
        move(translation): Moves the object by the specified translation.
        rotate(rotation, origin="local"): Rotates the object by the specified rotation.
        delete(): Deletes the object from the scene.
    """

    def __init__(self, object=None):
        """
        Initializes a new Object instance.

        Args:
            object (bpy.types.Object, optional): The Blender object to associate with this Object instance.
        """
        self._blender_object = object

    @property
    def blender_object(self):
        """
        The Blender object associated with this Object instance.

        Returns:
            bpy.types.Object: The Blender object.
        """
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
        """
        Sets the Blender object associated with this Object instance.

        Args:
            blender_object (bpy.types.Object): The Blender object to associate with this Object instance.
        """
        self._blender_object = blender_object

    @property
    def location(self):
        """
        The location of the object.

        Returns:
            list: The location as a list of coordinates [x, y, z].
        """
        return list(self.blender_object.location)

    @location.setter
    def location(self, location):
        """
        Sets the location of the object.

        Args:
            location (list): The new location as a list of coordinates [x, y, z].
        """
        self.blender_object.location = Vector(location)

    @property
    def position(self):
        """
        The position of the object.

        Returns:
            list: The position as a list of coordinates [x, y, z].
        """
        return self.location

    @position.setter
    def position(self, position):
        """
        Sets the position of the object.

        Args:
            position (list): The new position as a list of coordinates [x, y, z].
        """
        self.location = Vector(position)

    @property
    def rotation(self):
        """
        The rotation of the object.

        Returns:
            list: The rotation as a list of angles [x, y, z] in degrees.
        """
        return [degrees(angle) for angle in self.blender_object.rotation_euler]

    @rotation.setter
    def rotation(self, rotation):
        """
        Sets the rotation of the object.

        Args:
            rotation (list): The new rotation as a list of angles [x, y, z] in degrees.
        """
        self.blender_object.rotation_euler = Euler(
            [radians(angle) for angle in rotation], "XYZ"
        )

    @property
    def name(self):
        """
        The name of the object.

        Returns:
            str: The name of the object.
        """
        return self.blender_object.name

    @name.setter
    def name(self, name):
        """
        Sets the name of the object.

        Args:
            name (str): The new name of the object.
        """
        self.blender_object.name = name
        for object in bpy.data.objects.values():
            if object.name == name and object.data is not None:
                object.data.name = name

    def make_active(self):
        """
        Makes the object active in the scene.
        """
        bpy.ops.object.select_all(action="DESELECT")
        self.blender_object.select_set(True)
        bpy.context.view_layer.objects.active = self.blender_object

    def move(self, translation):
        """
        Moves the object by the specified translation.

        Args:
            translation (list): The translation as a list of coordinates [x, y, z].
        """
        self.location = Vector(self.blender_object.location) + Vector(translation)

    def rotate(self, rotation, origin="local"):
        """
        Rotates the object by the specified rotation.

        Args:
            rotation (list): The rotation as a list of angles [x, y, z] in degrees.
            origin (str or tuple or list or Vector or Object or bpy.types.Object, optional):
                The origin of the rotation. Defaults to "local".
                Possible values:
                - "local": Rotate around the object's local origin.
                - "cursor": Rotate around the 3D cursor.
                - "global" or "world" or "origin": Rotate around the global origin (0, 0, 0).
                - (x, y, z): Rotate around the specified point.
                - Object: Rotate around the location of the specified object.
        """
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

    def insert_keyframe(self, property, value, frame):
        """
        Inserts a keyframe for the specified property at the specified frame.

        Args:
            property (str): The name of the property to animate.
            value (float): The value of the property at the keyframe.
            frame (int): The frame at which to insert the keyframe.
        """
        if property in ("location", "position"):
            self.location = value
            self.blender_object.keyframe_insert(data_path="location", frame=frame)
        elif property in ("rotation"):
            self.rotation = value
            self.blender_object.keyframe_insert(data_path="rotation_euler", frame=frame)

    def delete(self):
        """
        Deletes the object from the scene.
        """
        a = 1
        if self.blender_object is not None:
            bpy.data.objects.remove(self.blender_object, do_unlink=True)
            self._blender_object = None
