from pathlib import Path

import bpy
from ase.calculators.vasp import VaspChargeDensity
from numpy import diag, tile

from .lib import flip_normals, marching_cubes_gaussian, marching_cubes_VASP, read_cube
from .meshobject import MeshObject
from .collection import Collection
from .material import Material
from .preset import Preset


class Isosurface(MeshObject):
    """
    Represents an isosurface object in Blender.

    Args:
        isosurface_object (object): The isosurface object.
        collection (Collection, optional): The collection to which the isosurface object belongs.
    """

    def __init__(self, isosurface_object, collection=None):
        self._isosurface_object = isosurface_object

        self._collection = collection
        self._link()
        super().__init__()

        if Preset.get("isosurface.remesh"):
            self.remesh()

    @classmethod
    def read(cls, filename, name=None, level=None, format=None):
        """
        Reads an isosurface from a file.

        Args:
            filename (str): The path to the file.
            name (str, optional): The name of the isosurface object.
            level (float, optional): The isosurface level.
            format (str, optional): The file format.

        Returns:
            Isosurface: The created Isosurface object.

        Raises:
            ValueError: If the file format is not supported.
        """
        filename = Path(filename)
        if name is None:
            name = filename.stem

        if format is None:
            format = filename.suffix if filename.suffix else filename.stem

        if format == ".cube":
            return Isosurface(CubeIsosurface(filename, name, level))
        elif format.lower() in ("parchg", "chgcar", "vasp", ".vasp"):
            return Isosurface(VaspIsosurface(filename, name, level))
        else:
            raise ValueError(f"Unsupported file format: {format}")

    @property
    def blender_object(self):
        """
        The Blender object associated with the isosurface.

        Returns:
            object: The Blender object.
        """
        return self._isosurface_object.blender_object

    @blender_object.setter
    def blender_object(self, blender_object):
        """
        Sets the Blender object associated with the isosurface.

        Args:
            blender_object (object): The Blender object.
        """
        self._isosurface_object.blender_object = blender_object

    @property
    def level(self):
        """
        The isosurface level.

        Returns:
            float: The isosurface level.
        """
        return self._isosurface_object.level

    @level.setter
    def level(self, level):
        """
        Sets the isosurface level.

        Args:
            level (float): The isosurface level.
        """
        self._isosurface_object.level = level
        self.update()

    @property
    def name(self):
        """
        The name of the isosurface object.

        Returns:
            str: The name of the isosurface object.
        """
        return self._isosurface_object.blender_object.name

    @name.setter
    def name(self, name):
        """
        Sets the name of the isosurface object.

        Args:
            name (str): The name of the isosurface object.
        """
        self._isosurface_object.blender_object.name = name

    def remesh(self):
        """
        Remeshes the isosurface object.
        """
        remesh_modifier = self.blender_object.modifiers.new(
            name="Remesh", type="REMESH"
        )
        remesh_modifier.mode = "VOXEL"
        remesh_modifier.use_smooth_shade = Preset.get("isosurface.smooth")
        remesh_modifier.voxel_size = Preset.get("isosurface.voxel_size")

    def repeat(self, repetitions):
        """
        Repeats the isosurface object.

        Args:
            repetitions (tuple): The repetitions in each direction.
        """
        self._isosurface_object.repetitions = repetitions
        self.update()
        self._isosurface_object.repetitions = (0, 0, 0)

    def update(self):
        """
        Updates the isosurface object.
        """
        name = self.name
        material = self.material
        self._unlink()
        self.blender_object = self._isosurface_object._create_mesh()
        self._link()
        self.name = name
        self.material = material
        if Preset.get("isosurface.remesh"):
            self.remesh()

    def _unlink(self):
        """
        Unlinks the isosurface object from the collection.
        """
        if self._collection is not None:
            bpy.data.collections[self._collection.name].objects.unlink(
                self.blender_object
            )
        else:
            bpy.data.collections["Collection"].objects.unlink(self.blender_object)
        bpy.data.objects.remove(self.blender_object, do_unlink=True)

    def _link(self):
        """
        Links the isosurface object to the collection.
        """
        if self._collection is not None:
            bpy.data.collections[self._collection.name].objects.link(
                self.blender_object
            )
        else:
            bpy.data.collections["Collection"].objects.link(self.blender_object)
        flip_normals(self.blender_object)


class VaspIsosurface:
    """
    Represents a VASP isosurface.

    Args:
        filename (str): The path to the VASP file.
        name (str): The name of the isosurface object.
        level (float, optional): The isosurface level.
        repetitions (tuple, optional): The repetitions in each direction.

    Attributes:
        name (str): The name of the isosurface object.
        level (float): The isosurface level.
        repetitions (tuple): The repetitions in each direction.
        density (numpy.ndarray): The charge density.
        unit_cell (numpy.ndarray): The unit cell.
        blender_object (object): The Blender object associated with the isosurface.

    Methods:
        _create_mesh(): Creates the mesh for the isosurface.
    """

    def __init__(self, filename, name, level=None, repetitions=(0, 0, 0)):
        self.name = name
        self.level = level
        self.repetitions = repetitions
        self.density = VaspChargeDensity(filename).chg[-1]
        self.unit_cell = VaspChargeDensity(filename).atoms[-1].cell
        self.blender_object = self._create_mesh()

    def _create_mesh(self):
        """
        Creates the mesh for the isosurface.

        Returns:
            object: The Blender object representing the isosurface.
        """
        if self.repetitions != (0, 0, 0):
            repetitions = tuple([repetition + 1 for repetition in self.repetitions])
            self.unit_cell = diag(repetitions) @ self.unit_cell
            self.density = tile(self.density, repetitions)

        return marching_cubes_VASP(self.density, self.unit_cell, self.name, self.level)


class CubeIsosurface:
    """
    Represents a cube isosurface.

    Args:
        filename (str): The path to the cube file.
        name (str): The name of the isosurface object.
        level (float, optional): The isosurface level.
        repetitions (tuple, optional): The repetitions in each direction.

    Attributes:
        name (str): The name of the isosurface object.
        level (float): The isosurface level.
        repetitions (tuple): The repetitions in each direction.
        density (numpy.ndarray): The charge density.
        origin (numpy.ndarray): The origin of the cube.
        axes (numpy.ndarray): The axes of the cube.
        blender_object (object): The Blender object associated with the isosurface.

    Methods:
        _create_mesh(): Creates the mesh for the isosurface.
    """

    def __init__(self, filename, name, level=None, repetitions=(0, 0, 0)):
        self.name = name
        self.level = level
        self.repetitions = repetitions
        self.density, self.origin, self.axes, *_ = read_cube(filename)
        self.blender_object = self._create_mesh()

    def _create_mesh(self):
        """
        Creates the mesh for the isosurface.

        Returns:
            object: The Blender object representing the isosurface.
        """
        if self.repetitions != (0, 0, 0):
            repetitions = tuple([repetition + 1 for repetition in self.repetitions])
            self.density = tile(self.density, repetitions)

        return marching_cubes_gaussian(
            self.density, self.origin, self.axes, self.name, self.level
        )


class ChargeDensity(Isosurface):
    """
    Represents a charge density isosurface.

    Args:
        *args: Variable length arguments.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        positive (Isosurface): The positive charge density isosurface.
        level (float): The isosurface level.
        name (str): The name of the isosurface object.
        blender_object (object): The Blender object associated with the isosurface.

    Methods:
        read(cls, *args, **kwargs): Reads an isosurface.
    """

    def __init__(self, *args, **kwargs):
        self.positive = Isosurface.read(*args, **kwargs)
        self.positive.material = Material(
            f'ChargeDensity - {Preset.get("isosurface.chargedensity.material")}'
        )

    @classmethod
    def read(cls, *args, **kwargs):
        """
        Reads an isosurface.

        Args:
            *args: Variable length arguments.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Isosurface: The created Isosurface object.
        """
        return ChargeDensity(*args, **kwargs)

    @property
    def level(self):
        """
        The isosurface level.

        Returns:
            float: The isosurface level.
        """
        return self.positive.level

    @level.setter
    def level(self, level):
        """
        Sets the isosurface level.

        Args:
            level (float): The isosurface level.
        """
        self.positive.level = level
        self.positive.update()

    @property
    def name(self):
        """
        The name of the isosurface object.

        Returns:
            str: The name of the isosurface object.
        """
        return self.positive._name

    @name.setter
    def name(self, name):
        """
        Sets the name of the isosurface object.

        Args:
            name (str): The name of the isosurface object.
        """
        self.positive._name = name

    @property
    def blender_object(self):
        """
        The Blender object associated with the isosurface.

        Returns:
            object: The Blender object.
        """
        return self.positive.blender_object

    @blender_object.setter
    def blender_object(self, blender_object):
        """
        Sets the Blender object associated with the isosurface.

        Args:
            blender_object (object): The Blender object.
        """
        self.positive.blender_object = blender_object

    def repeat(self, repetitions):
        """
        Repeats the isosurface.

        Args:
            repetitions (tuple): The repetitions in each direction.
        """
        self.positive.repeat(repetitions)


class Wavefunction:
    """
    Represents a wavefunction.

    Args:
        filename (str): The path to the wavefunction file.
        *args: Variable length arguments.
        name (str, optional): The name of the wavefunction.
        **kwargs: Arbitrary keyword arguments.

    Attributes:
        positive (Isosurface): The positive isosurface.
        negative (Isosurface): The negative isosurface.
        collection (Collection): The collection containing the wavefunction.

    Methods:
        read(cls, *args, **kwargs): Reads a wavefunction.
    """

    def __init__(self, filename, *args, name=None, **kwargs):
        name = Path(filename).stem if name is None else name
        self.collection = Collection(name)

        if "level" not in kwargs or kwargs["level"] is None:
            kwargs["level"] = 0.05

        kwargs["name"] = f"{name} - Positive"
        self.positive = Isosurface.read(filename, *args, **kwargs)
        kwargs["level"] = -self.positive.level
        self.positive.material = Material(
            f'Wavefunction (Positive) - {Preset.get("isosurface.wavefunction.negative.material")}'
        )
        kwargs["name"] = f"{name} - Negative"
        self.negative = Isosurface.read(filename, *args, **kwargs)
        self.negative.material = Material(
            f'Wavefunction (Negative) - {Preset.get("isosurface.wavefunction.negative.material")}'
        )
        self.negative._collection = self.collection
        self.positive._collection = self.collection

        self.collection.add(self.positive)
        self.collection.add(self.negative)

    @classmethod
    def read(cls, *args, **kwargs):
        """
        Reads a wavefunction.

        Args:
            *args: Variable length arguments.
            **kwargs: Arbitrary keyword arguments.

        Returns:
            Wavefunction: The created Wavefunction object.
        """
        return Wavefunction(*args, **kwargs)

    @property
    def level(self):
        """
        The isosurface levels.

        Returns:
            tuple: The isosurface levels.
        """
        return (self.positive.level, self.negative.level)

    @level.setter
    def level(self, level):
        """
        Sets the isosurface levels.

        Args:
            level (float): The isosurface level.
        """
        self.positive.level = level
        self.negative.level = -level
        self.positive.update()
        self.negative.update()

    @property
    def name(self):
        """
        The name of the wavefunction.

        Returns:
            str: The name of the wavefunction.
        """
        return self.collection.name

    @name.setter
    def name(self, name):
        """
        Sets the name of the wavefunction.

        Args:
            name (str): The name of the wavefunction.
        """
        self.collection.name = name
        self.positive.name = f"{name} - Positive"
        self.negative.name = f"{name} - Negative"

    @property
    def scale(self):
        """
        The scales of the isosurfaces.

        Returns:
            tuple: The scales of the isosurfaces.
        """
        return (self.positive.scale, self.negative.scale)

    @scale.setter
    def scale(self, scale):
        """
        Sets the scales of the isosurfaces.

        Args:
            scale (float): The scale of the isosurfaces.
        """
        self.positive.scale = scale
        self.negative.scale = scale

    @property
    def blender_object(self):
        """
        The Blender objects associated with the isosurfaces.

        Returns:
            tuple: The Blender objects associated with the isosurfaces.
        """
        return (self.positive.blender_object, self.negative.blender_object)

    @blender_object.setter
    def blender_object(self, blender_objects):
        """
        Sets the Blender objects associated with the isosurfaces.

        Args:
            blender_objects (tuple): The Blender objects associated with the isosurfaces.
        """
        self.positive.blender_object = blender_objects[0]
        self.positive.blender_object = blender_objects[1]

    def repeat(self, repetitions):
        """
        Repeats the isosurfaces.

        Args:
            repetitions (tuple): The repetitions in each direction.
        """
        self.positive.repeat(repetitions)
        self.negative.repeat(repetitions)
