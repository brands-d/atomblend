from json import load
from os.path import exists
from pathlib import Path

import bpy

from .periodic_table import PeriodicTable


class Material:
    materials_directory = Path(__file__).parent / "resources" / "materials"

    def __init__(self, name):
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
        return self._material

    @material.setter
    def material(self, material):
        self._material = material

    @classmethod
    def load(cls, name):

        try:
            file = str(Material.materials_directory / f"materials.blend")
            return Material._load(file, name)
        except KeyError:
            file = str(Material.materials_directory / f"materials.blend")
            return Material._load(file, name)

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

    @classmethod
    def _load(cls, file, name):
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
