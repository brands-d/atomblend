from os.path import exists
from pathlib import Path

import bpy

from .periodic_table import PeriodicTable


class Material:
    """A class representing a material in Blender."""

    materials_directory = Path(__file__).parent / "resources" / "materials"

    def __init__(self, name):
        """
        Initialize a Material object.

        Args:
            name (str): The name of the material.

        Raises:
            KeyError: If the material is not found.
        """
        if len(name) <= 2:
            try:
                name = PeriodicTable[name].name
            except KeyError:
                name = "Unknown"

        material = bpy.data.materials.get(name)
        if material is None:
            try:
                material = Material.load(name)
            except KeyError:
                print("Material not found. Creating new material.")
                material = Material.create(name)

        self._material = material

    @property
    def material(self):
        """
        Get the material object.

        Returns:
            bpy.types.Material: The material object.
        """
        return self._material

    @material.setter
    def material(self, material):
        """
        Set the material object.

        Args:
            material (bpy.types.Material): The material object.
        """
        self._material = material

    @classmethod
    def load(cls, name):
        """
        Load a material from file.

        Args:
            name (str): The name of the material.

        Returns:
            bpy.types.Material: The loaded material.

        Raises:
            KeyError: If the material is not found.
            RuntimeError: If the material file is not found.
        """
        try:
            file = str(Material.materials_directory / f"materials_user.blend")
            return Material._load(file, name)
        except (KeyError, RuntimeError):
            file = str(Material.materials_directory / f"materials.blend")
            return Material._load(file, name)

    @classmethod
    def create(cls, name, properties={}):
        """
        Create a new material.

        Args:
            name (str): The name of the material.
            properties (dict): Additional properties for the material.

        Returns:
            bpy.types.Material: The created material.
        """
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        material.use_backface_culling = True
        material.blend_method = "BLEND"
        node = material.node_tree.nodes["Principled BSDF"]

        for key, value in properties.items():
            try:
                node.inputs[key].default_value = value
            except KeyError:
                pass

    def edit(self, property, value):
        """
        Edit a property of the material.

        Args:
            property (str): The property to edit.
            value (any): The new value for the property.
        """
        try:
            shader = self._material.node_tree.nodes["Principled BSDF"]
        except KeyError:
            for node in self._material.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    shader = node
                    break
            if shader is None:
                raise KeyError("Principled BSDF node not found.")

        try:
            shader.inputs[property].default_value = value
        except KeyError:
            raise KeyError(f"Property {property} not found.")

    @classmethod
    def _load(cls, file, name):
        """
        Load a material from file.

        Args:
            file (str): The path to the material file.
            name (str): The name of the material.

        Returns:
            bpy.types.Material: The loaded material.

        Raises:
            KeyError: If the material is not found.
            RuntimeError: If the material file is not found.
        """
        if not exists(file):
            raise RuntimeError(f"{file} not found")

        try:
            bpy.ops.wm.append(
                filepath="/Material/" + name,
                filename=name,
                directory=file + "/Material/",
            )
        except RuntimeError:
            raise KeyError(f"Material {name} not found")

        material = bpy.data.materials.get(name)
        if material is None:
            raise KeyError(f"Material {name} not found")
        else:
            return material
