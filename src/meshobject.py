import bpy

from .material import Material
from .object import Object


class MeshObject(Object):
    """
    A class representing an mesh-like object in Blender. Not intended to be instantiated directly by the user but it is an interface implemented by all mesh-like objects like atoms, bonds and isosurfaces.
    """

    def __init__(self):
        """
        Initializes a new MeshObject instance.
        """

        super().__init__()
        self.modifiers = []
        self.blender_object = bpy.context.active_object

    @property
    def scale(self):
        """Current absolute scale of the mesh object.

        Note:
            Scale is identical to the scale setting inside the Blender UI. The size of the object also depends on the unscaled size at creation time.

        Returns:
            list: The scale as a list of three float values [x, y, z].
        """
        return list(self.blender_object.scale)

    @scale.setter
    def scale(self, scale):
        """Scales the mesh object.

        Warning:
            This will not set the absolute scale of an object but rather scale it by a multiplicative factor. This is for ease of use as one is usually interested in scaling an object by a factor rather than setting the absolute scale. Additionally, this way all mesh-objects can be scaled by a common factor at the same time without dealing with the absolute scale of each object.

        Args:
            scale (float | list | tuple | ndarray | Vector): The scale value(s) to set.
        """
        if isinstance(scale, (int, float)):
            scale = [scale] * 3
        self.blender_object.scale = [s * a for s, a in zip(self.scale, scale)]

    @property
    def material(self):
        """The material of the mesh object.

        Returns:
            Material: The material of the mesh object.
        """
        return Material(self.blender_object.active_material.name)

    @material.setter
    def material(self, material):
        """Set the material of the mesh object.

        Args:
            material (Material | str): The material to set. Can be the material directly or the name of the material.
        """

        if isinstance(Material, str):
            material = Material(material)

        self.blender_object.active_material = material.material

    def subsurface_modifier(self, viewport, render):
        """
        Adds a subsurface division modifier to the object.

        Args:
            viewport (int): How many subdivision are used for the viewport.
            render (int): How many subdivision are used for the render.
        """
        self.modifiers.append(
            self.blender_object.modifiers.new(name="Subsurface", type="SUBSURF")
        )
        self.modifiers[-1].levels = viewport
        self.modifiers[-1].render_levels = render

    def make_smooth(self):
        """
        Use the smooth shader for this object.
        """
        self.blender_object.data.polygons.foreach_set(
            "use_smooth",
            [True] * len(self.blender_object.data.polygons),
        )

    def insert_keyframe(self, frame=None):
        """
        Inserts a keyframe for the position, rotation scale of the object at frame.

        Args:
            frame (int | None): The frame to insert the keyframe. Defaults: None. If None, the current frame is used.
        """
        super().insert_keyframe(frame)

        if frame is not None:
            self.blender_object.keyframe_insert(
                data_path="scale", options=set(("INSERTKEY_NEEDED",)), frame=frame
            )
        else:
            self.blender_object.keyframe_insert(
                data_path="scale", options=set(("INSERTKEY_NEEDED",))
            )

    def remove_keyframe(self, frame=None):
        """
        Removes the keyframe for the position, rotation and scale of the object at frame.

        Args:
            frame (int | None): The frame to remove the keyframe. Defaults: None. If None, the current frame is used.
        """
        super().remove_keyframe(frame)
        if frame is not None:
            self.blender_object.keyframe_delete(data_path="scale", frame=frame)

        else:
            self.blender_object.keyframe_delete(data_path="scale")
