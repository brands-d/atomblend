import logging
from os.path import exists
from pathlib import Path

import bpy

from .periodic_table import PeriodicTable


class Material:
    """A class representing a material in Blender."""

    materials_directory = Path(__file__).parent / "resources" / "materials"

    def __init__(self, name):
        """
        Get an existing Blender material object. If the material does not exist, tries to load it from a materials file. User file is preferred. If the material is not found in any file, creates a new material.

        Args:
            name (str): The name of the material.
        """
        if len(name) <= 2:
            try:
                name = PeriodicTable[name].name
            except KeyError:
                name = "Unknown"

        material = bpy.data.materials.get(name)
        if material is None:
            try:
                Material._load(name)
            except (ValueError, RuntimeError):
                logging.warning(f"Material {name} not found. Creating a new material.")
                Material._create(name)

        self._material = bpy.data.materials.get(name)

    @property
    def name(self):
        """
        Get the name of the material.

        Returns:
            str: The name of the material.
        """
        return self._material.name

    @name.setter
    def name(self, name):
        """
        Set the name of the material.

        Args:
            name (str): The name of the material.
        """
        self._material.name = name

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
    def _create(cls, name):
        material = bpy.data.materials.new(name=name)
        material.use_nodes = True
        material.use_backface_culling = True
        material.blend_method = "BLEND"
        material.node_tree.nodes["Principled BSDF"]

    @property
    def properties(self):
        """
        Get the properties of the material.

        Note:
            Only possible if material has a Principled BSDF node.

        Returns:
            dict: The properties of the material.

        Raises:
            RuntimeError: Principled BSDF node is not found.
        """
        properties = {}
        try:
            shader = self._material.node_tree.nodes["Principled BSDF"]
        except KeyError:
            for node in self._material.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    shader = node
                    break
            if shader is None:
                raise RuntimeError("Principled BSDF node not found")

        for input in shader.inputs:
            properties[input.name] = input.default_value

        return properties

    @properties.setter
    def properties(self, properties):
        """
        Set the properties of the material.

        Note:
            Only possible to Principled BSDF node properties.

        Args:
            properties (dict): The properties to set.

        Raises:
            RuntimeError: Principled BSDF node is not found.
        """
        try:
            shader = self._material.node_tree.nodes["Principled BSDF"]
        except KeyError:
            for node in self._material.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    shader = node
                    break
            if shader is None:
                raise RuntimeError("Principled BSDF node not found")

        for property, value in properties.items():
            try:
                shader.inputs[property].default_value = value
            except KeyError:
                raise KeyError(f"Property {property} not found")

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
    def _load(cls, name):
        """
        Load a material from material files. User file is preferred.

        Args:
            name (str): The name of the material to load.

        Raises:
            RuntimeError: If the material file is not found.
            ValueError: If the specified material is not found in the file.
        """

        def _load_from_file(file, name):
            if not exists(file):
                raise RuntimeError(f"{file} not found")

            try:
                bpy.ops.wm.append(
                    filepath="/Material/" + name,
                    filename=name,
                    directory=file + "/Material/",
                )
            except RuntimeError:
                raise RuntimeError(f"Materials file {file} not found.")

            material = bpy.data.materials.get(name)
            if material is None:
                raise ValueError(f"Material {name} not found.")

        try:
            file = str(Material.materials_directory / f"materials_user.blend")
            _load_from_file(file, name)
        except (ValueError, RuntimeError):
            try:
                file = str(Material.materials_directory / f"materials.blend")
                _load_from_file(file, name)
            except (ValueError, RuntimeError):
                raise ValueError(f"Material file not found.")
