import bpy  # type: ignore

from .object import Object
from .preset import Preset


class Camera(Object):
    """
    A class representing a camera in Blender. Multiple cameras with different properties are possible.
    """

    first_camera = True

    def __init__(self, name=None, position=(0, 0, 10), rotation=(0, 0, 0)):
        """
        Initialize a new camera object.

        Args:
            name (str): Name of the new camera. Default: Camera[.xxx].
            position (tuple | list | ndarray | Vector): The position of the camera in 3D space. Default: (0, 0, 10).
            rotation (tuple | list | ndarray | Vector): The rotation of the camera in Euler angles. Default: (0, 0, 0).
        """

        # The first camera is a reference to already existing camera
        if Camera.first_camera:
            self.blender_object = Camera._get_scene_camera()
        else:
            self.blender_object = Camera._new()

        self.position = position
        self.rotation = rotation
        self.resolution = Preset.get("camera.resolution")
        self.lens = Preset.get("camera.lens")
        self.render_engine = Preset.get("camera.render_engine")

        if self.lens == "perspective":
            self.focuslength = Preset.get("camera.focuslength")
        elif self.lens == "orthographic":
            self.orthographic_scale = Preset.get("camera.orthographic_scale")

        if name is not None:
            self.name = name

        self.active = True
        Camera.first_camera = False

    @property
    def resolution(self):
        """
        Get the resolution of the camera.

        Returns:
            tuple[int, int]: The resolution of the camera in pixels, as a tuple (width, height).
        """
        if self.active:
            self._resolution = (
                bpy.context.scene.render.resolution_x,
                bpy.context.scene.render.resolution_y,
            )
        return self._resolution

    @resolution.setter
    def resolution(self, resolution):
        """
        Set the resolution of the camera.

        Args:
            resolution (tuple[int, int]): The resolution of the camera in pixels, as a tuple (width, height).
        """
        self._resolution = resolution
        if self.active:
            bpy.context.scene.render.resolution_x = self._resolution[0]
            bpy.context.scene.render.resolution_y = self._resolution[1]

    @property
    def focuslength(self):
        """
        Get the focuslength of the camera.

        Returns:
            float: The focuslength of the camera.

        Raises:
            TypeError: Focuslength only defined for perspective cameras.
        """
        if self.lens != "perspective":
            raise TypeError(
                "Wrong camera type. Focuslength only for perspective cameras."
            )
        return self.blender_object.data.lens

    @focuslength.setter
    def focuslength(self, focuslength):
        """
        Set the focuslength of the camera.

        Args:
            focuslength (float): The focus length of the camera.

        Raises:
            TypeError: Focuslength only defined for perspective cameras.
        """
        if self.lens != "perspective":
            raise TypeError(
                "Wrong camera type. Focuslength only for perspective cameras."
            )

        self.blender_object.data.lens = focuslength

    @property
    def orthographic_scale(self):
        """
        Get the orthographic scale of the camera.

        Returns:
            float: The orthographic scale of the camera.

        Raises:
            TypeError: Orthographic scale only defined for orthographic cameras.
        """
        if self.lens != "orthographic":
            raise TypeError(
                "Wrong camera type. Orthographic scale only for orthographic cameras."
            )
        return self.blender_object.data.ortho_scale

    @orthographic_scale.setter
    def orthographic_scale(self, orthographic_scale):
        """
        Set the orthographic scale of the camera.

        Args:
            orthographic scale (float): The orthographic scale of the camera.

        Raises:
            TypeError: Orthographic scale only defined for orthographic cameras.
        """
        if self.lens != "orthographic":
            raise TypeError(
                "Wrong camera type. Orthographic scale only for orthographic cameras."
            )

        self.blender_object.data.ortho_scale = orthographic_scale

    @property
    def lens(self):
        """
        Returns the type of lens used by the camera.

        Returns:
            str: The type of lens used by the camera. Possible values are "perspective", "orthographic", or "panoramic".
        """
        lens = self.blender_object.data.type
        if lens == "PERSP":
            return "perspective"
        elif lens == "ORTHO":
            return "orthographic"
        elif lens == "PANO":
            return "panoramic"
        else:
            raise RuntimeError("Unknown camera type encountered.")

    @lens.setter
    def lens(self, lens):
        """
        Set the lens type for the camera.

        Args:
            lens (str): The type of lens to set. {"orthographic", "perspective", "panoramic"}

        Raises:
            ValueError: If the provided lens type is unknown.
        """
        if lens[:5].lower() == "persp":
            self.blender_object.data.type = "PERSP"
        elif lens[:5].lower() == "ortho":
            self.blender_object.data.type = "ORTHO"
        elif lens[:4].lower() == "pano":
            self.blender_object.data.type = "PANO"
        else:
            raise ValueError("Unknown lens type.")

    @property
    def active(self):
        """
        Get whether the camera is the active scene camera.

        Returns:
            bool: Whether camera is the active scene camera.
        """
        return bpy.context.scene.camera == self.blender_object

    @active.setter
    def active(self, value):
        """
        Make a camera the active scene camera.

        Note:
            Only accepts TRUE. Can not make unassign camera as scene camera. Instead make a different camera active camera.

        Args:
            TRUE: Only TRUE allowed. Makes camera active camera.

        Raises:
            ValueError: Do not pass a FALSE value. See note.
        """
        if not value:
            raise ValueError(
                "Can not make camera inactive. Instead make a different camera active."
            )

        resolution = self.resolution
        bpy.context.scene.camera = self.blender_object
        self.resolution = resolution

    def render(filepath=None, show=True, mode="quality"):
        """
        Renders the current scene using the specified rendering mode and saves the image to a file.

        Parameters:
        - filepath (str): The path to save the rendered image. If None, the image will not be saved.
        - show (bool): Whether to display the rendered image in a separate window.
        - mode (str): The rendering mode to use. Options are "fast", "performance", "eevee" for fast rendering,
        and "slow", "quality", "beautiful", "cycles" for high-quality rendering.
        """
        original_display_type = bpy.context.preferences.view.render_display_type
        if show:
            bpy.context.preferences.view.render_display_type = "WINDOW"

        engine = bpy.context.scene.render.engine
        if mode.lower() in ["fast", "performance", "eevee"]:
            bpy.context.scene.render.engine = "BLENDER_EEVEE"
        elif mode.lower() in ["slow", "quality", "beautiful", "cycles"]:
            bpy.context.scene.render.engine = "CYCLES"

        if filepath is not None:
            bpy.context.scene.render.filepath = str(filepath)
            if show:
                bpy.ops.render.render("INVOKE_DEFAULT", write_still=True)
            else:
                bpy.ops.render.render(write_still=True)
        else:
            if show:
                bpy.ops.render.render("INVOKE_DEFAULT")
            else:
                bpy.ops.render.render()

        bpy.context.scene.render.engine = engine
        bpy.context.preferences.view.render_display_type = original_display_type

    @classmethod
    def _get_scene_camera(cls):
        """
        Returns the active scene camera. If no camera is assigned to the scene, a new one is generated and added to the scene.

        Returns:
            bpy.Camera: The blender object of the active scene camera.
        """
        camera = bpy.context.scene.camera
        if camera is None:
            # No camera assigned to scene
            for object in bpy.data.objects:
                # Try to find a existing camera object
                if object.type == "CAMERA":
                    bpy.context.scene.camera = object
                    return object
            # None found
            return Camera._new().blender_object
        else:
            return camera

    @classmethod
    def _new(cls):
        """
        Creates a new camera blender object.

        Returns:
            bpy.Camera: The blender object of the new camera.
        """
        camera = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
        bpy.context.collection.objects.link(camera)

        return camera
