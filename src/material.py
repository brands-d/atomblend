from pathlib import Path
from json import load

import bpy

from .periodic_table import PeriodicTable


class Material:
    custom_material_directory = (
        Path(__file__).parent / "resources" / "materials_user.blend"
    )

    preset_material_directory = Path(__file__).parent / "resources" / "materials.blend"

    def __init__(self, name):
        if len(name) <= 2:
            try:
                name = PeriodicTable[name].name
            except KeyError:
                name = "Unknown"

        material = bpy.data.materials.get(name)
        if material is None:
            try:
                Material.load_preset_material(name)
            except KeyError:
                pass

        material = bpy.data.materials.get(name)
        if material is None:
            try:
                Material.load_preset_material(name, custom=False)
            except KeyError:
                pass

        material = bpy.data.materials.get(name)
        if material is None:
            print("Material not found. Creating new material.")
            material = Material.create(name)

        self._material = material

    @property
    def material(self):
        return self._material

    @material.setter
    def material(self, material):
        self._material = material

    @classmethod
    def load_preset_material(cls, name, custom=True):
        if custom:
            directory = str(Material.custom_material_directory) + "/Material/"
        else:
            directory = str(Material.preset_material_directory) + "/Material/"

        bpy.ops.wm.append(
            filepath="/Material/" + name,
            filename=name,
            directory=directory,
        )
        material = bpy.data.materials.get(name)

        if material is None:
            raise KeyError(f"Material {name} not found")
        else:
            return material

    @classmethod
    def create(cls, name, properties={}):
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
