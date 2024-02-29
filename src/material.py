import logging
from os.path import exists
from pathlib import Path

import bpy

from .periodic_table import PeriodicTable


class Material:
    """A class representing a material in Blender.

    Attributes:
        materials_directory (Path): The directory where the material files are located.
        materials_user_file (Path): The file containing the user materials.
        materials_file (Path): The file with the default materials.
    """

    materials_directory = Path(__file__).parent / "resources" / "materials"
    materials_user_file = materials_directory / f"materials_user.blend"
    materials_file = materials_directory / f"materials.blend"

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

    @property
    def color(self):
        """
        Base color of the material.

        Returns:
            tuple[float]: RGBA values between 0 and 1.
        """
        try:
            return self.properties["Base Color"]
        except KeyError:
            try:
                return self.properties["Color"]
            except KeyError:
                return (1, 1, 1, 1)

    @color.setter
    def color(self, color):
        """
        Sets the base color of the material.

        Args:
            color (tuple[float]): RGBA values between 0 and 1.
        """
        self.properties = {"Base Color": color}

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
            shader = None
            for node in self._material.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    shader = node
                    break
                elif node.type == "BSDF_GLOSSY":
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

    @property
    def shader(self):
        """
        Get the shader node of the material.

        Returns:
            bpy.types.Node: The shader node.
        """
        try:
            return self._material.node_tree.nodes["Principled BSDF"]
        except KeyError:
            for node in self._material.node_tree.nodes:
                if node.type == "BSDF_PRINCIPLED":
                    return node
                elif node.type == "BSDF_GLOSSY":
                    return node
            return None

    @property
    def node_group(self):
        """
        Get nodes of a material as a node group with a shader output.

        Note:
            Only works for materials with nodes and ONE principled BSDF node or ONE glossy BSDF node.

        Returns:
            bpy.types.Node: The node group.

        Raises:
            RuntimeError: Material does not use nodes.
        """
        if not self.material.use_nodes:
            raise RuntimeError("Material does not use nodes.")

        group = bpy.data.node_groups.new(
            name=f"{self.name} Group", type="ShaderNodeTree"
        )
        group_out = group.nodes.new(type="NodeGroupOutput")

        node_mapping = {}

        for node in self.material.node_tree.nodes:
            if node.type != "OUTPUT_MATERIAL":
                new_node = group.nodes.new(type=node.bl_idname)
                if (
                    node.bl_idname == "ShaderNodeBsdfPrincipled"
                    or node.bl_idname == "ShaderNodeBsdfGlossy"
                ):
                    shader = node
                new_node.name = node.name
                for input in node.inputs:
                    try:
                        new_node.inputs[input.name].default_value = input.default_value
                    except KeyError:
                        pass
                node_mapping[node] = new_node

        for link in self.material.node_tree.links:
            if link.to_node.type != "OUTPUT_MATERIAL":
                from_node = node_mapping[link.from_node]
                to_node = node_mapping[link.to_node]
                from_socket = from_node.outputs[link.from_socket.name]
                to_socket = to_node.inputs[link.to_socket.name]
                group.links.new(from_socket, to_socket)

        group.interface.new_socket(
            name="Shader",
            in_out="OUTPUT",
            socket_type="NodeSocketShader",
        )
        group.links.new(node_mapping[shader].outputs["BSDF"], group_out.inputs[0])

        return group

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
            _load_from_file(str(Material.materials_user_file), name)
        except (ValueError, RuntimeError):
            try:
                _load_from_file(str(Material.materials_file), name)
            except (ValueError, RuntimeError):
                raise ValueError(f"Material file not found.")
