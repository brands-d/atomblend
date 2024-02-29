import logging
from itertools import combinations, product
from pathlib import Path

import bpy  # type: ignore
from ase.calculators.vasp import VaspChargeDensity
from ase.io import read as aread
from mathutils import Vector  # type: ignore
from numpy import diag, ndarray

from .bond import Bond
from .collection import Collection
from .material import Material
from .meshobject import MeshObject
from .object import Object
from .periodic_table import PeriodicTable
from .preset import Preset
from .animation import Animation


class Atom(MeshObject):
    """
    Represents a single atom.

    Attributes:
        covalent_radius (float): The covalent radius of the atom. This is used to determine the bond length.
        element (str): The chemical symbol of the atom.
    """

    _atoms = []

    def __init__(self, element="X"):
        """
        Initializes a new instance of the Atom class.

        The atom is created as a uv sphere with a radius based on the radius
        defined PeriodicTable.

        Args:
            element (str): The chemical symbol of the atom. Default: "X".

        Examples:
            >>> # This will create a new atom hydrogen atom.
            >>> atom = Atom("H")
        """

        radius = PeriodicTable[element].radius
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius * Atom._get_preset("size", element),
            segments=Atom._get_preset("quality.segments", element),
            ring_count=Atom._get_preset("quality.rings", element),
        )
        super().__init__()

        if Atom._get_preset("quality.smooth", element):
            self.make_smooth()

        self.subsurface_modifier(
            Atom._get_preset("quality.viewport", element),
            Atom._get_preset("quality.render", element),
        )

        self.covalent_radius = PeriodicTable[element].covalent_radius
        self.element = element
        self.name = element
        self.material = Material(
            f'{PeriodicTable[element].name} - {Atom._get_preset("material",element)}'
        )
        self.bonds = []
        Atom._atoms.append(self)

    @classmethod
    def ase(cls, atom: "ase.Atom"):
        """
        Creates an Atom instance from an ASE Atom object.

        Args:
            atom (ase.Atom): The ASE Atom object.

        Returns:
            Atom: The created Atom instance.

        Examples:
            >>> # This will create a new atom hydrogen atom.
            >>> atom = Atom.ase(ase.Atom("H"))
        """

        try:
            self = Atom(str(atom.symbols))
            self.location = atom.positions[0]
        except AttributeError:
            self = Atom(str(atom.symbol))
            self.location = atom.position

        return self

    @classmethod
    def get(cls, filter=None):
        """
        Retrieves a list of atoms existing in the entire scene based on the
        specified filter.

        The filter can be a simple element symbol or a callable that takes an
        Atom object as an argument and returns a boolean.

        Default returns all atoms.

        Note:
            Use `and` and `or` to combine multiple conditions into complex
            filters.

        Args:
            filter (str | callable): The filter to apply. Default: None.

        Returns:
            list[Atom]: The list of atoms that match the filter.

        Examples:
            >>> # This will return all atoms in the scene.
            >>> Atom.get()
            >>> # This will return all carbon atoms in the scene.
            >>> Atom.get("C")
            >>> # This will return all atoms with a z-coordinate greater than 10.
            >>> Atom.get(lambda atom: atom.location[2] > 10)
        """

        Atom._clean()

        if filter is None or filter == "all":
            return cls._atoms
        elif isinstance(filter, str) and len(filter) <= 2:
            return [atom for atom in cls._atoms if atom.element == filter]
        elif callable(filter):
            return [atom for atom in cls._atoms if filter(atom)]

    @classmethod
    def _clean(cls):
        """
        Removes atoms that have been deleted from the scene via UI.
        """

        for atom in cls._atoms:
            if atom.blender_object is None:
                cls._atoms.remove(atom)

    def __add__(self, other):
        """
        Adds two atoms together to form a new `Atoms` object or will add the
        atom to an existing atoms object.

        Args:
            other (Atom | Atoms): The other atom or atoms collection to add.

        Returns:
            Atoms: The resulting atoms collection.
        """

        if isinstance(other, Atom):
            atoms = Atoms("New Atoms")
            atoms += self
            atoms += other
            return atoms
        elif isinstance(other, Atoms):
            other += self
            return other

    def delete(self):
        """
        Deletes the atom.
        """

        self._atoms.remove(self)
        super().delete()

    @classmethod
    def _get_preset(self, setting, element):
        """
        Retrieves the value of a specific property for a specific element. If not set uses global atoms setting.

        Args:
            setting (str): The property to retrieve.
            element (str): The element symbol.

        Returns:
            any: The value of the property in the preset.
        """
        try:
            return Preset.get(f"atoms.{element}.{setting}")
        except KeyError:
            return Preset.get(f"atoms.{setting}")


class Atoms(MeshObject):
    """
    Represents a collection of atoms in a 3D scene. This could be a molecule or a surface.
    """

    def __init__(self, name):
        """
        Initializes a new instance of the Atoms class.

        Args:
            name (str): The name of the atoms collection.

        Examples:
            >>> # This will create a new atoms collection.
            >>> atoms = Atoms("Water")
        """

        self._atoms = []
        self._unit_cell = None
        self.copies = []

        self.collection = Collection(name)
        self.atoms_collection = Collection("Atoms")
        self.collection.link(self.atoms_collection)
        self.bonds_collection = Collection("Bonds")
        self.collection.link(self.bonds_collection)

    @classmethod
    def ase(cls, atoms, name=None):
        """
        Creates an Atoms instance from an ASE Atoms object.

        Args:
            atoms (ase.Atoms): The ASE Atoms object.
            name (str | None): The name of the atoms collection. Default: None. "New Atoms".

        Returns:
            Atoms: The created Atoms instance.

        Examples:
            >>> # This will create a new atoms collection from an ASE Atoms object.
            >>> atoms = Atoms.ase(ase.Atoms("H2O"))
        """

        if name is None:
            name = "New Atoms"
        self = Atoms(name)
        self.unit_cell = atoms.cell[:]
        for atom in atoms:
            self += Atom.ase(atom)

        self.create_bonds()
        return self

    @classmethod
    def read(cls, filename, name=None, format=None):
        """
        Reads an atoms collection from a file.

        Args:
            filename (str): The path to the file.
            name (str | None): The name of the atoms collection. Default: None. Name of the file.
            format (str): The file format. Default: None. Guess format.

        Returns:
            Atoms: The read atoms collection.

        Examples:
            >>> # This will read an atoms collection from a file. Does not create bonds between substrate atoms.
            >>> atoms = Atoms.read("POSCAR")
        """

        filename = Path(filename)
        if name is None:
            name = filename.stem

        if format is not None:
            format = format.lower()

        if filename.stem == "CHGCAR" or format in ("chgcar", "parchg"):
            atoms = VaspChargeDensity(str(filename)).atoms[-1]
            return Atoms.ase(atoms, name)
        elif (
            filename.stem in ("XDATCAR")
            or format == "vasp-xdatcar"
            or filename.suffix == ".traj"
        ):
            format = "" if filename.suffix == ".traj" else "vasp-xdatcar"
            for frame, aux in enumerate(aread(str(filename), format=format, index=":")):
                frame = frame * Preset.get("animation.frame_multiplier")
                animation = Animation()
                if frame == 0:
                    atoms = Atoms.ase(aux, name)

                animation.current_frame = frame
                atoms.insert_keyframe(aux.positions)

            animation.final_frame = frame
            return atoms
        else:
            return Atoms.ase(aread(str(filename), format=format), name=name)

    def __add__(self, objects):
        """
        Adds an atom or bond to the atoms collection.

        Args:
            objects (Atom or Bond or list[Atom or Bond]): The atom or bond, or a list of atoms or bonds to add.

        Returns:
            Atoms: The updated atoms collection.
        """

        if not isinstance(objects, (list, tuple)):
            objects = (objects,)
        for object in objects:
            if isinstance(object, Atom):
                _ = self.atoms_collection + object
                self._atoms.append(object)
            elif isinstance(object, Bond):
                _ = self.bonds_collection + object

        return self

    @property
    def atoms(self):
        """
        Gets the atoms collection.

        Returns:
            Collection: The atoms collection.
        """

        return self.atoms_collection

    @property
    def bonds(self):
        """
        Gets the bonds collection.

        Returns:
            Collection: The bonds collection.
        """
        return self.bonds_collection

    @property
    def name(self):
        """
        Gets or sets the name of the atoms collection.

        Returns:
            str: The name of the atoms collection.
        """
        return self.collection.name

    @name.setter
    def name(self, name):
        """
        Sets the name of the atoms collection.

        Args:
            name (str): The name of the atoms collection.
        """
        self.collection.name = name

    @property
    def unit_cell(self):
        """
        Gets or sets the unit cell of the atoms collection.

        Returns:
            ndarray or None: The unit cell of the atoms collection.
        """
        return self._unit_cell

    @unit_cell.setter
    def unit_cell(self, cell):
        """
        Sets the unit cell of the atoms collection.

        Args:
            cell (ndarray or list or tuple or Vector): The unit cell of the atoms collection.
        """
        if isinstance(cell[0], (ndarray, tuple, Vector, list)):
            self._unit_cell = cell
        else:
            self._unit_cell = diag(cell)

    @property
    def scale(self):
        """
        Gets or sets the scale of the atoms collection.

        Returns:
            float: The scale of the atoms collection.
        """
        return (self.atoms_collection.scale, self.bonds_collection.scale)

    @scale.setter
    def scale(self, scale):
        """
        Sets the scale of the atoms collection.

        Args:
            scale (float): The scale of the atoms collection.
        """
        self.atoms_collection.scale = scale
        self.bonds_collection.scale = scale

    @property
    def material(self):
        """
        Gets or sets the material of the atoms collection.

        Returns:
            Material: The material of the atoms collection.
        """
        return (self.atoms_collection.material, self.bonds_collection.material)

    @material.setter
    def material(self, material):
        """
        Sets the material of the atoms collection.

        Args:
            material (Material): The material of the atoms collection.
        """
        self.atoms_collection.material = material
        self.bonds_collection.material = material

    @property
    def origin(self):
        """
        Gets or sets the origin of the atoms collection.

        Returns:
            Vector: The origin of the atoms collection.
        """
        return (self.atoms_collection.origin, self.bonds_collection.origin)

    @origin.setter
    def origin(self, origin):
        """
        Sets the origin of the atoms collection.

        Args:
            origin (Vector): The origin of the atoms collection.
        """
        self.atoms_collection.origin = origin
        self.bonds_collection.origin = origin

    @property
    def location(self):
        """
        Gets or sets the location of the atoms collection.

        Returns:
            Vector: The location of the atoms collection.
        """
        return (self.atoms_collection.location, self.bonds_collection.location)

    @location.setter
    def location(self, location):
        """
        Sets the location of the atoms collection.

        Args:
            location (Vector): The location of the atoms collection.
        """
        self.atoms_collection.location = location
        self.bonds_collection.location = location

    def get(self, filter=None):
        """
        Retrieves a list of atoms based on the specified filter.

        Args:
            filter (str or callable, optional): The filter to apply. Defaults to None.

        Returns:
            list[Atom]: The list of atoms that match the filter.
        """
        self.clean()

        if filter is None or filter == "all":
            return self._atoms
        elif isinstance(filter, str) and len(filter) <= 2:
            return [atom for atom in self._atoms if atom.element == filter]
        elif callable(filter):
            return [atom for atom in self._atoms if filter(atom)]

    def move(self, translation):
        """
        Moves the atoms collection by the specified translation.

        Args:
            translation (Vector): The translation to apply.
        """
        self.atoms_collection.move(translation)
        self.bonds_collection.move(translation)

    def rotate(self, rotation, origin=None):
        """
        Rotates the atoms collection by the specified rotation.

        Args:
            rotation (Quaternion or Euler or Matrix): The rotation to apply.
            origin (Vector, optional): The origin of the rotation. Defaults to None.
        """
        self.atoms_collection.rotate(rotation, origin)
        self.bonds_collection.rotate(rotation, origin)

    def clean(self):
        """
        Removes atoms that no longer have a Blender object associated with them.
        """
        for atom in self._atoms:
            if atom.blender_object is None:
                self._atoms.remove(atom)

    def create_bonds(self, periodic=True):
        """
        Creates bonds between atoms in the atoms collection.

        Args:
            periodic (bool): Whether to consider periodic boundaries. Default: True.
        """
        exclude_bonds = Preset.get("bonds.no_bonds")

        if periodic and self.unit_cell is None:
            logging.warning("Cannot do periodic bonds without unit cell.")
            periodic = False

        for atom_a, atom_b in combinations(self.get("all"), 2):
            if [atom_a.element, atom_b.element] in exclude_bonds or [
                atom_b.element,
                atom_a.element,
            ] in exclude_bonds:
                continue

            if periodic:
                for x, y, z in (p for p in product((-1, 0, 1), repeat=3)):
                    shift = Vector(
                        x * self.unit_cell[0]
                        + y * self.unit_cell[1]
                        + z * self.unit_cell[2]
                    )

                    if (x, y, z) != (0, 0, 0):
                        atom_b_dummy = _DummyAtom(atom_b)
                        atom_b_dummy.position = Vector(atom_b.position) + shift
                        self._create_bond(atom_a, atom_b_dummy)
                    else:
                        self._create_bond(atom_a, atom_b)
            else:
                self._create_bond(atom_a, atom_b)

    def _create_bond(self, atom_a, atom_b):
        """
        Creates a bond between two atoms if there distance is smaller or equal to bonds.factor * (atom_a.covalent_radius + atom_b.covalent_radius)

        Args:
            atom_a (Atom): The first atom.
            atom_b (Atom): The second atom.
        """
        if Bond._check_distance(atom_a, atom_b):
            self += Bond(atom_a, atom_b)

    def repeat(self, repetitions):
        """
        Creates copies of the atoms collection based on the specified repetitions.

        Args:
            repetitions (tuple[int, int, int]): The number of repetitions in each direction.
        """

        if repetitions == (0, 0, 0):
            return
        else:
            if self.unit_cell is None:
                raise RuntimeError("No unit cell defined.")

            self.copies_collection = Collection(f"{self.name} Copies")
            repetitions = [
                range(min(0, repetition), max(0, repetition) + 1)
                for repetition in repetitions
            ]
            for x in repetitions[0]:
                for y in repetitions[1]:
                    for z in repetitions[2]:
                        if x == 0 and y == 0 and z == 0:
                            continue
                        copy = self._new_instance_to_scene(
                            f"{self.name} - ({x:d}, {y:d}, {z:d})"
                        )
                        copy.location = (
                            x * Vector(self.unit_cell[0])
                            + y * Vector(self.unit_cell[1])
                            + z * Vector(self.unit_cell[2])
                        )
                        self.copies.append(copy)

    def insert_keyframe(self, positions):
        """
        Inserts a keyframe for the specified property at the specified frame.

        Args:
            ase
        """

        for atom, position in zip(self.atoms, positions):
            atom.position = position
            atom.insert_keyframe()

        for bond in self.bonds:
            bond.update()
            bond.insert_keyframe()

    def _new_instance_to_scene(self, name):
        """
        Creates a new instance of the atoms collection in the scene.

        Args:
            name (str): The name of the instance.

        Returns:
            Object: The created instance.
        """

        instance = Object()
        instance.blender_object = bpy.data.objects.new(name=name, object_data=None)
        instance.blender_object.instance_type = "COLLECTION"
        instance.blender_object.instance_collection = self.collection.collection
        self.copies_collection + instance

        return instance


class _DummyAtom:
    """
    Represents a dummy atom used for creating bonds in periodic systems.
    """

    def __init__(self, atom):
        """
        Initializes a new instance of the _DummyAtom class.

        Args:
            atom (Atom): The original atom.
        """
        self.atom = atom
        self.covalent_radius = atom.covalent_radius
        self.position = atom.position
        self.name = atom.name

    @property
    def position(self):
        """
        Position of the atom.

        Returns:
            Vector: Position of the atom.
        """
        return Vector(self.atom.position) + Vector(self._shift)

    @position.setter
    def position(self, value):
        """
        Sets the position of the atom.

        Args:
            value (Vector): The new position of the atom.
        """
        self._shift = Vector(value) - Vector(self.atom.position)

    @property
    def material(self):
        """
        Material of the atom.

        Returns:
            Material: Material of the atom.
        """
        return self.atom.material

    @property
    def bonds(self):
        """
        Returns the bonds associated with this atom.

        Returns:
            list: A list of bonds associated with this atom.
        """
        return self.atom.bonds
