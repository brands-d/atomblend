import bpy  # type: ignore

from .object import Object


class Camera(Object):
    """
    A class representing a camera object in Blender.
    """

    _blender_object = None

    def __init__(self, position=(0, 0, 10), rotation=(0, 0, 0)):
        """
        Initialize a Camera object.

        Args:
            position (tuple, optional): The position of the camera in 3D space. Defaults to (0, 0, 10).
            rotation (tuple, optional): The rotation of the camera in Euler angles. Defaults to (0, 0, 0).
        """
        if self.blender_object is None:
            self.blender_object = bpy.context.scene.camera

        self.position = position
        self.rotation = rotation
        self.resolution = (1080, 1080)

    @property
    def blender_object(self):
        """
        Get the Blender camera object associated with this Camera.

        Returns:
            bpy.types.Object: The Blender camera object.
        """
        return Camera._blender_object

    @blender_object.setter
    def blender_object(self, blender_object):
        """
        Set the Blender camera object associated with this Camera.

        Args:
            blender_object (bpy.types.Object): The Blender camera object.
        """
        Camera._blender_object = blender_object

    @property
    def resolution(self):
        """
        Get the resolution of the camera.

        Returns:
            tuple: The resolution of the camera in pixels, as a tuple (width, height).
        """
        return (
            bpy.context.scene.render.resolution_x,
            bpy.context.scene.render.resolution_y,
        )

    @resolution.setter
    def resolution(self, resolution):
        """
        Set the resolution of the camera.

        Args:
            resolution (tuple): The resolution of the camera in pixels, as a tuple (width, height).
        """
        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]

    @property
    def focuslength(self):
        """
        Get the focus length of the camera.

        Returns:
            float: The focus length of the camera.
        """
        return self._blender_object.lens

    @focuslength.setter
    def focuslength(self, focuslength):
        """
        Set the focus length of the camera.

        Args:
            focuslength (float): The focus length of the camera.
        """
        self._blender_object.lens = focuslength
