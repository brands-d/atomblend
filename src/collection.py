import bpy
from mathutils import Vector
from numpy import ndarray

from .object import Object


class Collection:
    def __init__(self, name="New Collection"):
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
        return self.collection.name

    @name.setter
    def name(self, name):
        self.collection.name = name

    @property
    def objects(self):
        self._sync()
        return self._objects

    @property
    def scale(self):
        scales = []
        for object in self.objects:
            try:
                scales.append(list(object.scale))
            except Exception:
                pass

        return scales

    @scale.setter
    def scale(self, scale):
        # if not isinstance(scale, (list, tuple)):
        #    scale = [scale] * 3
        for object in self.objects:
            try:
                object.scale = scale
                # object.scale = [s * a for s, a in zip(object.scale, scale)]
            except Exception:
                pass

    @property
    def material(self):
        materials = []
        for object in self.objects:
            try:
                materials.append(object.material)
            except Exception:
                pass

        return materials

    @material.setter
    def material(self, material):
        for object in self.objects:
            try:
                object.material = material
            except Exception:
                pass

    @property
    def origin(self):
        self.origin = self._origin_type
        return self._origin

    @origin.setter
    def origin(self, origin):
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
        locations = []
        for object in self.objects:
            locations.append(object.location)

        return locations

    @location.setter
    def location(self, location):
        translation = Vector(location) - self.origin
        self.move(translation)

    @property
    def position(self):
        return self.location

    @position.setter
    def position(self, position):
        self.location = Vector(position)

    @property
    def rotation(self):
        pass

    @rotation.setter
    def rotation(self, rotation):
        pass

    def __add__(self, objects):
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
        if not isinstance(objects, (list, tuple)):
            objects = (objects,)
        for object in objects:
            self.objects.remove(object)
            self.collection.objects.unlink(object.blender_object)

        self._sync()
        return self

    def __getitem__(self, index):
        return self.objects[index]

    def move(self, translation):
        for object in self.objects:
            object.move(translation)

    def rotate(self, rotation, origin=None):
        if origin is not None:
            self.origin = origin

        for object in self.objects:
            object.rotate(rotation, self.origin)

    def add(self, objects):
        self + objects

    def link(self, collection):
        try:
            self.collection.children.link(collection.collection)
            bpy.context.scene.collection.children.unlink(collection.collection)
        except RuntimeError:
            pass

    def remove(self, objects):
        self - objects

    def dissolve(self):
        for object in self.collection.objects:
            bpy.context.scene.collection.objects.link(object)
            self.collection.objects.unlink(object)

        bpy.data.collections.remove(self.collection)

    def _unlink_from_scene_collections(self, object):
        for collection in bpy.context.scene.collection.children:
            if collection.name != self.collection.name:
                if object.name in collection.objects:
                    collection.objects.unlink(object)

        if object.name in bpy.context.scene.collection.objects:
            bpy.context.scene.collection.objects.unlink(object)

    def _sync(self):
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
        for object in self.collection.objects:
            object.delete()
        bpy.data.collections.remove(self.collection)
