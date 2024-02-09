import bpy
from mathutils import Vector
from numpy import ndarray

from .object import Object


class Collection:
    """
    Represents a collection of objects in Blender.
    """

    def __init__(self, name="New Collection"):
        """
        Initializes a new Collection object.

        Args:
            name (str): The name of the collection.
        """
        self._objects = []
        self._origin = Vector([0, 0, 0])
        self._origin_type = "center"

        if name in bpy.data.collections:
            self.collection = bpy.data.collections[name]
        else:
            self.collection = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(self.collection)

    @property
    def name(self):
        """
        The name of the collection.

        Returns:
            str: The name of the collection.
        """
        return self.collection.name

    @name.setter
    def name(self, name):
        """
        Sets the name of the collection.

        Args:
            name (str): The new name for the collection.
        """
        self.collection.name = name

    @property
    def objects(self):
        """
        The objects in the collection.

        Returns:
            list: A list of Object instances representing the objects in the collection.
        """
        self._sync()
        return self._objects

    @property
    def scale(self):
        """
        The scale of the objects in the collection.

        Returns:
            list: A list of scales for each object in the collection.
        """
        scales = []
        for object in self.objects:
            try:
                scales.append(list(object.scale))
            except Exception:
                pass

        return scales

    @scale.setter
    def scale(self, scale):
        """
        Sets the scale of the objects in the collection.

        Args:
            scale (float or list): The new scale value or a list of scale values for each axis.
        """
        for object in self.objects:
            try:
                object.scale = scale
            except Exception:
                pass

    @property
    def material(self):
        """
        The material of the objects in the collection.

        Returns:
            list: A list of materials for each object in the collection.
        """
        materials = []
        for object in self.objects:
            try:
                materials.append(object.material)
            except Exception:
                pass

        return materials

    @material.setter
    def material(self, material):
        """
        Sets the material of the objects in the collection.

        Args:
            material: The new material for the objects in the collection.
        """
        for object in self.objects:
            try:
                object.material = material
            except Exception:
                pass

    @property
    def origin(self):
        """
        The origin point of the collection.

        Returns:
            Vector: The origin point of the collection.
        """
        self.origin = self._origin_type
        return self._origin

    @origin.setter
    def origin(self, origin):
        """
        Sets the origin point of the collection.

        Args:
            origin (list, tuple, ndarray, Vector, Object, str): The new origin point.
        """
        self._origin_type = origin
        if isinstance(origin, (list, tuple, ndarray, Vector)):
            self._origin = Vector(origin)
        elif isinstance(origin, Object):
            self._origin = Vector(origin.location)
        elif isinstance(origin, str):
            if origin.lower() in ("world", "origin"):
                self._origin = Vector((0, 0, 0))
            elif origin.lower() in ("cursor"):
                self._origin = bpy.context.scene.cursor.location.copy()
            elif origin.lower() in ("center"):
                max_ = []
                min_ = []
                for i in range(3):
                    aux = []
                    for object in self.objects:
                        aux.append(object.location[i])
                    max_.append(max(aux))
                    min_.append(min(aux))

                self._origin = Vector(
                    [(upper + lower) / 2 for upper, lower in zip(max_, min_)]
                )
            else:
                object = None
                for o in self.objects:
                    if o.name == origin:
                        object = o
                        break
                if object is None:
                    raise ValueError
                else:
                    self._origin = Vector(object.location)

    @property
    def location(self):
        """
        The location of the objects in the collection.

        Returns:
            list: A list of locations for each object in the collection.
        """
        locations = []
        for object in self.objects:
            locations.append(object.location)

        return locations

    @location.setter
    def location(self, location):
        """
        Sets the location of the objects in the collection.

        Args:
            location (list, tuple, ndarray, Vector): The new location for the objects.
        """
        translation = Vector(location) - self.origin
        self.move(translation)

    @property
    def position(self):
        """
        The position of the objects in the collection.

        Returns:
            list: A list of positions for each object in the collection.
        """
        return self.location

    @position.setter
    def position(self, position):
        """
        Sets the position of the objects in the collection.

        Args:
            position (list, tuple, ndarray, Vector): The new position for the objects.
        """
        self.location = Vector(position)

    @property
    def rotation(self):
        """
        The rotation of the objects in the collection.

        Returns:
            None: The rotation property is not implemented yet.
        """
        pass

    @rotation.setter
    def rotation(self, rotation):
        """
        Sets the rotation of the objects in the collection.

        Args:
            rotation: The new rotation for the objects.
        """
        pass

    def __add__(self, objects):
        """
        Adds objects to the collection.

        Args:
            objects (Object or list): The object(s) to add to the collection.
        """
        self._sync()
        if not isinstance(objects, (list, tuple)):
            objects = (objects,)
        for object in objects:
            self.collection.objects.link(object.blender_object)
            self._objects.append(object)
            self._unlink_from_scene_collections(object.blender_object)

        self._sync()
        return self

    def __sub__(self, objects):
        """
        Removes objects from the collection.

        Args:
            objects (Object or list): The object(s) to remove from the collection.
        """
        if not isinstance(objects, (list, tuple)):
            objects = (objects,)
        for object in objects:
            self.objects.remove(object)
            self.collection.objects.unlink(object.blender_object)

        self._sync()
        return self

    def __getitem__(self, index):
        """
        Retrieves an object from the collection by index.

        Args:
            index (int): The index of the object to retrieve.

        Returns:
            Object: The object at the specified index.
        """
        return self.objects[index]

    def move(self, translation):
        """
        Moves the objects in the collection by a translation vector.

        Args:
            translation (Vector): The translation vector.
        """
        for object in self.objects:
            object.move(translation)

    def rotate(self, rotation, origin=None):
        """
        Rotates the objects in the collection.

        Args:
            rotation: The rotation to apply to the objects.
            origin (list, tuple, ndarray, Vector, Object, str): The origin point for the rotation.
        """
        if origin is not None:
            self.origin = origin

        for object in self.objects:
            object.rotate(rotation, self.origin)

    def add(self, objects):
        """
        Adds objects to the collection.

        Args:
            objects (Object or list): The object(s) to add to the collection.
        """
        self + objects

    def link(self, collection):
        """
        Links another collection to this collection.

        Args:
            collection (Collection): The collection to link.
        """
        try:
            self.collection.children.link(collection.collection)
            bpy.context.scene.collection.children.unlink(collection.collection)
        except RuntimeError:
            pass

    def remove(self, objects):
        """
        Removes objects from the collection.

        Args:
            objects (Object or list): The object(s) to remove from the collection.
        """
        self - objects

    def dissolve(self):
        """
        Dissolves the collection, moving its objects to the scene collection.
        """
        for object in self.collection.objects:
            bpy.context.scene.collection.objects.link(object)
            self.collection.objects.unlink(object)

        bpy.data.collections.remove(self.collection)

    def _unlink_from_scene_collections(self, object):
        """
        Unlinks an object from other collections in the scene.

        Args:
            object (bpy.types.Object): The object to unlink.
        """
        for collection in bpy.context.scene.collection.children:
            if collection.name != self.collection.name:
                if object.name in collection.objects:
                    collection.objects.unlink(object)

        if object.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(object)

    def _sync(self):
        """
        Synchronizes the internal list of objects with the collection's objects.
        """
        for object in self._objects:
            if (
                object.blender_object is not None
                and object.blender_object.name not in self.collection.objects
            ):
                self._objects.remove(object)

        for object in self.collection.objects:

            if object.name not in [
                object.blender_object.name for object in self._objects
            ]:
                self._objects.append(Object(object))

    def delete(self):
        """
        Deletes the collection and its objects from the scene.
        """
        for object in self.collection.objects:
            object.delete()
        bpy.data.collections.remove(self.collection)
