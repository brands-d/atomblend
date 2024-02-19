import bpy
from math import degrees, radians
from mathutils import Euler, Vector


class Object:
    """
    A class representing an object in Blender. Not intended to be instantiated directly by the user but it is an interface implemented by all objects inside the Blender scene and defines basic behavior common to all objects.
    """

    def __init__(self, object=None):
        """
        Initializes a new Object instance.

        Args:
            object (bpy.types.Object | None): The Blender object to associate with this Object instance.
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

        Note:
            Identical to the position property.

        Returns:
            list: The location as a list of cartessian coordinates [x, y, z].
        """
        return list(self.blender_object.location)

    @location.setter
    def location(self, location):
        """
        Sets the location of the object.

        Args:
            location (list | tuple | ndarray | Vector): The new location as a list-like object of cartessian coordinates.
        """
        self.blender_object.location = Vector(location)

    @property
    def position(self):
        """
        The position of the object.

        Note:
            Identical to the location property.

        Returns:
            list: The position as a list of cartessian coordinates [x, y, z].
        """
        return self.location

    @position.setter
    def position(self, position):
        """
        Sets the position of the object.

        Args:
            location (list | tuple | ndarray | Vector): The new location as a list-like object of cartessian coordinates.
        """
        self.location = Vector(position)

    @property
    def rotation(self):
        """
        The rotation of the object.

        Note:
            Rotation angles are identical to the ones used in the Blender interface.

        Returns:
            list: The rotation as a list of euler [x, y, z] in degrees.
        """
        return [degrees(angle) for angle in self.blender_object.rotation_euler]

    @rotation.setter
    def rotation(self, rotation):
        """
        Sets the rotation of the object.

        Args:
            rotation (list | tuple | ndarray | Vector): The new rotation as a list of euler angles [x, y, z] in degrees.
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

    @property
    def active(self):
        """
        Whether the object is active in the scene.

        Returns:
            bool: True if the object is active, False otherwise.
        """
        return self.blender_object == bpy.context.view_layer.objects.active

    @active.setter
    def active(self, value):
        """
        Sets the object as active in the scene.

        Note:
            Only accepts TRUE. Can not make an object inactive. Instead, make a different object active.

        Args:
            TRUE: Only TRUE allowed.

        Raises:
            ValueError: Do not pass a FALSE value. See note.
        """
        if not value:
            raise ValueError(
                "Can not make object inactive. Instead make a different object active."
            )

        bpy.ops.object.select_all(action="DESELECT")
        self.blender_object.select_set(True)
        bpy.context.view_layer.objects.active = self.blender_object

    def move(self, translation):
        """
        Moves the object by the specified translation.

        Args:
            translation (list | tuple | ndarray | Vector): The translation as a list of coordinates [x, y, z].
        """
        self.location = Vector(self.blender_object.location) + Vector(translation)

    def rotate(self, rotation, origin="local"):
        """
        Rotates the object by the specified rotation.

        Args:
            rotation (list): The rotation as a list of euler angles [x, y, z] in degrees.
            origin (str | tuple | list | ndarray | Vector | Object | bpy.types.Object):
                The origin of the rotation. Defaults to "local".
                Possible values:
                - "local": Rotate around the objects local origin.
                - "cursor": Rotate around the 3D cursor.
                - {"global", "world", "origin"}: Rotate around the global origin (0, 0, 0).
                - (x, y, z): Rotate around the specified point.
                - {Object bpy.data.Object}: Rotate around the location of the specified object.
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

            self.active()
            bpy.ops.object.origin_set(type="ORIGIN_CURSOR")
            self.rotation = Vector(rotation) + Vector(self.rotation)
            bpy.ops.object.origin_set(type="ORIGIN_GEOMETRY")
            bpy.context.scene.cursor.location = previous_cursor_location

    def insert_keyframe(self, frame=None):
        """
        Inserts a keyframe for the position and rotation of the object at frame.

        Args:
            frame (int | None): The frame to insert the keyframe. Defaults: None. If None, the current frame is used.
        """
        if frame is not None:
            self.blender_object.keyframe_insert(
                data_path="location", options=set(("INSERTKEY_NEEDED",)), frame=frame
            )
            self.blender_object.keyframe_insert(
                data_path="rotation_euler",
                options=set(("INSERTKEY_NEEDED",)),
                frame=frame,
            )
        else:
            self.blender_object.keyframe_insert(
                data_path="location", options=set(("INSERTKEY_NEEDED",))
            )
            self.blender_object.keyframe_insert(
                data_path="rotation_euler", options=set(("INSERTKEY_NEEDED",))
            )

    def remove_keyframe(self, frame=None):
        """
        Removes the keyframe for the position and rotation of the object at frame.

        Args:
            frame (int | None): The frame to remove the keyframe. Defaults: None. If None, the current frame is used.
        """
        if frame is not None:
            self.blender_object.keyframe_delete(data_path="location", frame=frame)
            self.blender_object.keyframe_delete(data_path="rotation_euler", frame=frame)
        else:
            self.blender_object.keyframe_delete(data_path="location")
            self.blender_object.keyframe_delete(data_path="rotation_euler")

    def delete(self):
        """
        Deletes the object from the scene.
        """
        if self.blender_object is not None:
            bpy.data.objects.remove(self.blender_object, do_unlink=True)
            self._blender_object = None
