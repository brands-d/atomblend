from itertools import combinations, product
from pathlib import Path
from typing import Union

import bpy  # type: ignore
from ase.calculators.vasp import VaspChargeDensity
from ase.io import read
from mathutils import Vector  # type: ignore
from numpy import diag, ndarray

from .bond import Bond
from .collection import Collection
from .material import Material
from .meshobject import MeshObject
from .object import Object
from .periodic_table import PeriodicTable
from .preset import Preset

# from .animation import get_frame_range, set_frame_range


class Atom(MeshObject):
    """
    Represents a single atom.

    Attributes:
        covalent_radius (float): The covalent radius of the atom. This is used to determine the bond length.
        element (str): The chemical symbol of the atom.
    """

    _atoms = []

    def __init__(self, element: str = "X") -> None:
        """
        Initializes a new instance of the Atom class.

        The atom is created as a uv sphere with a radius based on the radius
        defined in the :mod:`PeriodicTable`.

        Args:
            element (str, optional): The chemical symbol of the atom. Default: "X"

        Examples:
            >>> # This will create a new atom hydrogen atom.
            >>> atom = Atom("H")
        """

        radius = PeriodicTable[element].radius
        bpy.ops.mesh.primitive_uv_sphere_add(
            radius=radius * Preset.get("atoms.size"), segments=16, ring_count=8
        )
        super().__init__()

        self.blender_object.data.polygons.foreach_set(
            "use_smooth",
            [Preset.get("atoms.smooth")] * len(self.blender_object.data.polygons),
        )
        self.modifier = self.blender_object.modifiers.new(
            name="Subsurface", type="SUBSURF"
        )
        self.modifier.levels = Preset.get("atoms.viewport_quality")
        self.modifier.render_levels = Preset.get("atoms.render_quality")

        self.covalent_radius = PeriodicTable[element].covalent_radius
        self.element = element
        self.name = element
        self.material = Material(
            f'{PeriodicTable[element].name} - {Preset.get("atoms.material")}'
        )
        Atom._atoms.append(self)

    @classmethod
    def ase(cls, atom: "ase.Atom") -> "Atom":
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
    def get(cls, filter: Union[str, callable] = None) -> list["Atom"]:
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
            filter (str | callable, optional): The filter to apply. Default: None.

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

    def __add__(self, other: Union["Atom", "Atoms"]) -> "Atoms":
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

    def delete(self) -> None:
        """
        Deletes the atom.
        """

        self._atoms.remove(self)
        super().delete()


class Atoms(MeshObject):
    """
    Represents a collection of atoms in a 3D scene.
    """

    def __init__(self, name: str) -> None:
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
    def ase(
        cls,
        atoms: "ase.Atoms",
        name: str = None,
        exclude_bonds: Union[list, tuple] = None,
    ):
        """
        Creates an Atoms instance from an ASE Atoms object.

        Args:
            atoms (ase.Atoms): The ASE Atoms object.
            name (str, optional): The name of the atoms collection. Defaults to
            None.
            exclude_bonds (list, optional): A list of tuples of elements
            symbols to exclude from bond creation. Defaults to None.

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

        self.create_bonds(exclude_bonds=exclude_bonds)
        return self

    @classmethod
    def read(
        cls,
        filename: Union[str, Path],
        name: str = None,
        format: str = None,
        exclude_bonds: Union[list, tuple] = None,
    ):
        """
        Reads an atoms collection from a file.

        Args:
            filename (str): The path to the file.
            name (str, optional): The name of the atoms collection. Defaults to None.
            format (str, optional): The file format. Defaults to None.
            exclude_bonds (list, optional): A list of tuples of elements
            symbols to exclude from bond creation. Defaults to None.

        Returns:
            Atoms: The read atoms collection.

        Examples:
            >>> # This will read an atoms collection from a file. Does not create bonds between substrate atoms.
            >>> atoms = Atoms.read("POSCAR", exclude_bonds=("Ag", "Ag"))
        """

        filename = Path(filename)
        if name is None:
            name = filename.stem

        if filename.stem == "CHGCAR" or (
            isinstance(format, str) and format.lower in ("chgcar", "parchg")
        ):
            atoms = VaspChargeDensity(str(filename)).atoms[-1]
            return Atoms.ase(atoms, name)
        # elif (
        #     filename.stem in ("XDATCAR")
        #     or format == "vasp-xdatcar"
        #     or filename.suffix == ".traj"
        # ):
        #     final_frame = -1
        #     format = "traj" if filename.suffix == "traj" else "vasp-xdatcar"
        #     for frame, aux in enumerate(read(str(filename), format=format, index=":")):
        #         final_frame = frame
        #         if frame == 0:
        #             atoms = Atoms.ase(aux, name, exclude_bonds=exclude_bonds)

        #         atoms.insert_keyframe("location", aux.positions, frame)

        #     if get_frame_range()[-1] < final_frame:
        #         set_frame_range(get_frame_range()[0], frame)
        #     return atoms
        else:
            return Atoms.ase(
                read(str(filename), format=format),
                name=name,
                exclude_bonds=exclude_bonds,
            )

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

    def create_bonds(
        self, periodic: bool = True, exclude_bonds: Union[list, tuple] = None
    ):
        """
        Creates bonds between atoms in the atoms collection.

        Args:
            periodic (bool, optional): Whether to consider periodic boundaries.
            Defaults to True.
            exclude_bonds (list, optional): A list of tuples of elements
            symbols to exclude from bond creation. Defaults to None.
        """

        if exclude_bonds is not None and isinstance(exclude_bonds[0], str):
            exclude_bonds = (exclude_bonds,)
        for atom_1, atom_2 in combinations(self.get("all"), 2):
            if (
                exclude_bonds is not None
                and (atom_1.element, atom_2.element) in exclude_bonds
            ):
                continue
            if periodic and self.unit_cell is not None:
                for x, y, z in (p for p in product((-1, 0, 1), repeat=3)):
                    shift = Vector(
                        x * self.unit_cell[0]
                        + y * self.unit_cell[1]
                        + z * self.unit_cell[2]
                    )
                    if (
                        Vector(atom_1.position)
                        - Vector(atom_2.position)
                        - Vector(shift)
                    ).length <= 1.2 * (atom_1.covalent_radius + atom_2.covalent_radius):
                        if (x, y, z) != (0, 0, 0) and periodic:
                            atom_2 = _DummyAtom(atom_2)
                            atom_2.position = Vector(atom_2.position) + shift

                        self += Bond(atom_1, atom_2)
            else:
                if (Vector(atom_1.position) - Vector(atom_2.position)).length <= 1.2 * (
                    atom_1.covalent_radius + atom_2.covalent_radius
                ):
                    self += Bond(atom_1, atom_2)

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

    def insert_keyframe(self, property, values, frame, update_bonds=True):
        """
        Inserts a keyframe for the specified property at the specified frame.

        Args:
            property (str): The name of the property to animate.
            values (float): The values of the property at the keyframe.
            frame (int): The frame at which to insert the keyframe.
        """
        for atom, value in zip(self._atoms, values):
            atom.insert_keyframe(property, value, frame)

        if update_bonds:
            for bond in self.bonds:
                bond.update()
                bond.insert_keyframe("location", bond.location, frame)
                bond.insert_keyframe("rotation", bond.rotation, frame)

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
        self.position = atom.position
        self.covalent_radius = atom.covalent_radius
        self.name = atom.name
