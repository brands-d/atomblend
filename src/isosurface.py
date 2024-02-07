from pathlib import Path

import bpy
from ase.calculators.vasp import VaspChargeDensity
from numpy import diag, tile

from .lib import flip_normals, marching_cubes_gaussian, marching_cubes_VASP, read_cube
from .meshobject import MeshObject
from .collection import Collection


class Isosurface(MeshObject):
    def __init__(self, isosurface_object, collection=None):
        self._isosurface_object = isosurface_object
        self._collection = collection
        self._link()
        super().__init__()

    @classmethod
    def read(cls, filename, name=None, level=None, format=None):
        filename = Path(filename)
        if name is None:
            name = filename.stem

        if format is None:
            format = filename.suffix if filename.suffix else filename.stem

        if format == ".cube":
            return Isosurface(CubeIsosurface(filename, name, level))
        elif format.lower() in ("parchg", "chgcar"):
            return Isosurface(VaspIsosurface(filename, name, level))
        else:
            raise ValueError(f"Unsupported file format: {format}")

    @property
    def blender_object(self):
        return self._isosurface_object.blender_object

    @blender_object.setter
    def blender_object(self, blender_object):
        self._isosurface_object.blender_object = blender_object

    @property
    def level(self):
        return self._isosurface_object.level

    @level.setter
    def level(self, level):
        self._isosurface_object.level = level
        self.update()

    @property
    def name(self):
        return self._isosurface_object.blender_object.name

    @name.setter
    def name(self, name):
        self._isosurface_object.blender_object.name = name

    def repeat(self, repetitions):
        self._isosurface_object.repetitions = repetitions
        self.update()
        self._isosurface_object.repetitions = (0, 0, 0)

    def update(self):
        name = self.name
        self._unlink()
        self.blender_object = self._isosurface_object._create_mesh()
        self._link()
        self.name = name

    def _unlink(self):
        if self._collection is not None:
            bpy.data.collections[self._collection.name].objects.unlink(
                self.blender_object
            )
        else:
            bpy.data.collections["Collection"].objects.unlink(self.blender_object)
        bpy.data.objects.remove(self.blender_object, do_unlink=True)

    def _link(self):
        if self._collection is not None:
            bpy.data.collections[self._collection.name].objects.link(
                self.blender_object
            )
        else:
            bpy.data.collections["Collection"].objects.link(self.blender_object)
        flip_normals(self.blender_object)


class VaspIsosurface:
    def __init__(self, filename, name, level=None, repetitions=(0, 0, 0)):
        self.name = name
        self.level = level
        self.repetitions = repetitions
        self.density = VaspChargeDensity(filename).chg[-1]
        self.unit_cell = VaspChargeDensity(filename).atoms[-1].cell
        self.blender_object = self._create_mesh()

    def _create_mesh(self):
        if self.repetitions != (0, 0, 0):
            repetitions = tuple([repetition + 1 for repetition in self.repetitions])
            self.unit_cell = diag(repetitions) @ self.unit_cell
            self.density = tile(self.density, repetitions)

        return marching_cubes_VASP(self.density, self.unit_cell, self.name, self.level)


class CubeIsosurface:
    def __init__(self, filename, name, level=None, repetitions=(0, 0, 0)):
        self.name = name
        self.level = level
        self.repetitions = repetitions
        self.density, self.origin, self.axes, *_ = read_cube(filename)
        self.blender_object = self._create_mesh()

    def _create_mesh(self):
        if self.repetitions != (0, 0, 0):
            repetitions = tuple([repetition + 1 for repetition in self.repetitions])
            self.density = tile(self.density, repetitions)

        return marching_cubes_gaussian(
            self.density, self.origin, self.axes, self.name, self.level
        )


class ChargeDensity(Isosurface):
    def __init__(self, *args, **kwargs):
        self.positive = Isosurface.read(*args, **kwargs)

    @classmethod
    def read(cls, *args, **kwargs):
        return Wavefunction(*args, **kwargs)

    @property
    def level(self):
        return self.positive.level

    @level.setter
    def level(self, level):
        self.positive.level = level
        self.positive.update()

    @property
    def name(self):
        return self.positive._name

    @name.setter
    def name(self, name):
        self.positive._name = name

    @property
    def blender_object(self):
        return self.positive.blender_object

    @blender_object.setter
    def blender_object(self, blender_object):
        self.positive.blender_object = blender_object

    def repeat(self, repetitions):
        self.positive.repeat(repetitions)


class Wavefunction:
    def __init__(self, filename, *args, name=None, **kwargs):
        name = Path(filename).stem if name is None else name
        self.collection = Collection(name)

        if "level" not in kwargs or kwargs["level"] is None:
            kwargs["level"] = 0.05

        kwargs["name"] = f"{name} - Positive"
        self.positive = Isosurface.read(filename, *args, **kwargs)
        kwargs["level"] = -self.positive.level
        kwargs["name"] = f"{name} - Negative"
        self.negative = Isosurface.read(filename, *args, **kwargs)
        self.negative._collection = self.collection
        self.positive._collection = self.collection

        self.collection.add(self.positive)
        self.collection.add(self.negative)

    @classmethod
    def read(cls, *args, **kwargs):
        return Wavefunction(*args, **kwargs)

    @property
    def level(self):
        return (self.positive.level, self.negative.level)

    @level.setter
    def level(self, level):
        self.positive.level = level
        self.negative.level = -level
        self.positive.update()
        self.negative.update()

    @property
    def name(self):
        return self.collection.name

    @name.setter
    def name(self, name):
        self.collection.name = name
        self.positive.name = f"{name} - Positive"
        self.negative.name = f"{name} - Negative"

    @property
    def scale(self):
        return (self.positive.scale, self.negative.scale)

    @scale.setter
    def scale(self, scale):
        self.positive.scale = scale
        self.negative.scale = scale

    @property
    def blender_object(self):
        return (self.positive.blender_object, self.negative.blender_object)

    @blender_object.setter
    def blender_object(self, blender_objects):
        self.positive.blender_object = blender_objects[0]
        self.positive.blender_object = blender_objects[1]

    def repeat(self, repetitions):
        self.positive.repeat(repetitions)
        self.negative.repeat(repetitions)
