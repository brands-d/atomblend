import bpy  # type:ignore
from mathutils import Vector  # type:ignore
from math import acos, atan2, degrees

from .meshobject import MeshObject
from .material import Material
from .preset import Preset


class Bond(MeshObject):
    """
    Represents a bond between two atoms in a molecular structure.

    Attributes:
        atom_a (Atom): The first atom connected by the bond.
        atom_b (Atom): The second atom connected by the bond.
    """

    def __init__(self, atom_a, atom_b):
        """
        Initializes a Bond object between two atoms.

        Args:
            atom_a (Atom): The first atom connected by the bond.
            atom_b (Atom): The second atom connected by the bond.
        """
        self.atom_a = atom_a
        self.atom_b = atom_b
        self.atom_a.bonds.append(self)
        self.atom_b.bonds.append(self)

        vertices = Preset.get("bonds.sides")
        bpy.ops.mesh.primitive_cylinder_add(vertices=vertices)
        super().__init__()

        self.update()
        thickness = Preset.get("bonds.thickness")
        self.scale = (thickness, thickness, 1)

        self.material = Preset.get("bonds.material")
        self.name = f"{atom_a.name}-{atom_b.name}"

    @property
    def thickness(self):
        """
        Get the thickness of the bond. Corresponds to the scaling.

        Returns:
            float: Thickness of the bond.
        """
        return self.blender_object.scale[0]

    @thickness.setter
    def thickness(self, thickness):
        """
        Set the thickness of the bond.

        Args:
            scale (float): Sets the thickness of the bond.
        """

        self.blender_object.scale = [thickness, thickness, self.scale[1]]

    @property
    def material(self):
        """
        Returns the material of the bond.

        Returns:
            Material: Material of the bond.
        """
        return self.material

    @material.setter
    def material(self, material):
        """
        Sets the material for the bond.

        Args:
            material (str | Material): Can either be a material directly or a string. String can either be the name of a material or "step". "step" will create a bond with the colors of the atoms it connects. Middle point is dependent on the covalent radius ratio between the atoms.
        """

        if material in ("step",):
            material = Material(f"Bond - {material}")
            material.name = f"Bond - {self.name}"
            mix_shader_node = material.material.node_tree.nodes["Mix Shader"]
            color_ramp_node = material.material.node_tree.nodes["Color Ramp"]
            atom_a_group = material.material.node_tree.nodes.new("ShaderNodeGroup")
            atom_b_group = material.material.node_tree.nodes.new("ShaderNodeGroup")
            atom_a_group.node_tree = self.atom_a.material.node_group
            atom_b_group.node_tree = self.atom_b.material.node_group

            material.material.node_tree.links.new(
                atom_a_group.outputs["Shader"],
                mix_shader_node.inputs[2],
            )
            material.material.node_tree.links.new(
                atom_b_group.outputs["Shader"],
                mix_shader_node.inputs[1],
            )
            ratio = self.atom_b.covalent_radius / (
                self.atom_a.covalent_radius + self.atom_b.covalent_radius
            )
            color_ramp_node.color_ramp.elements[1].position = ratio
        elif isinstance(material, Material):
            pass
        else:
            material = Material(f"Bond - {material}")

        self.blender_object.active_material = material.material

    def update(self):
        """
        Update the position, rotation, and scale of the bond based on the positions of the connected atoms.
        """
        if not self._check_distance(self.atom_a, self.atom_b):
            self.hide(True)
        else:
            self.hide(False)

        distance = Vector(self.atom_a.position) - Vector(self.atom_b.position)
        location = Vector(self.atom_a.position) - distance / 2

        self.position = location
        self.rotation = (
            0,
            degrees(acos(distance[2] / distance.length)),
            degrees(atan2(distance[1], distance[0])),
        )
        self.blender_object.scale[2] = distance.length / 2

    @classmethod
    def _check_distance(cls, atom_a, atom_b):
        """
        Check if the distance between two atoms is within the bonding threshold.

        Args:
            atom_a (Atom): The first atom.
            atom_b (Atom): The second atom.

        Returns:
            bool: True if the distance is within the bonding threshold, False otherwise.
        """
        factor = Preset.get("bonds.factor")
        position_a = Vector(atom_a.position)
        position_b = Vector(atom_b.position)
        radius_a = atom_a.covalent_radius
        radius_b = atom_b.covalent_radius

        return (position_a - position_b).length <= factor * (radius_a + radius_b)

    def insert_keyframe(self, frame=None):
        """
        Inserts a keyframe for hiding the object in the viewport and render.

        Args:
            frame (int | None): The frame number to insert the keyframe. If not provided, the keyframe is inserted at the current frame.
        """
        if frame is not None:
            self.blender_object.keyframe_insert(data_path="hide_viewport", frame=frame)
            self.blender_object.keyframe_insert(data_path="hide_render", frame=frame)
        else:
            self.blender_object.keyframe_insert(data_path="hide_viewport")
            self.blender_object.keyframe_insert(data_path="hide_render")

        super().insert_keyframe(frame)

    def delete(self):
        """
        Removes itself from bond lists of atoms participating in bond.
        """
        self.atom_a.bonds.remove(self)
        self.atom_b.bonds.remove(self)

    def hide(self, hide):
        """
        Hides the bond in the viewport and render.

        Args:
            hide (bool): True if the bond should be hidden, False otherwise.
        """
        self.blender_object.hide_viewport = hide
        self.blender_object.hide_render = hide
