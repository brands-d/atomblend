from pathlib import Path
from functools import wraps

import bpy  # type: ignore

from .object import Object
from .preset import Preset


class Camera(Object):
    """
    A class representing a camera in Blender. Multiple cameras with different properties are possible.
    """

    first = True

    def __init__(self, name=None, position=(0, 0, 10), rotation=(0, 0, 0)):
        """
        Initialize a new camera object.

        Args:
            name (str): Name of the new camera. Default: Camera[.xxx].
            position (tuple | list | ndarray | Vector): The position of the camera in 3D space. Default: (0, 0, 10).
            rotation (tuple | list | ndarray | Vector): The rotation of the camera in Euler angles. Default: (0, 0, 0).
        """

        # The first camera is a reference to already existing camera
        if Camera.first:
            self.blender_object = Camera._get_scene_camera()
        else:
            self.blender_object = Camera._new()

        self.position = position
        self.rotation = rotation
        self.resolution = Preset.get("camera.resolution")
        self.lens = Preset.get("camera.lens")
        self.quality = Preset.get("camera.quality")

        if self.lens == "perspective":
            self.focuslength = Preset.get("camera.focuslength")
        elif self.lens == "orthographic":
            self.orthographic_scale = Preset.get("camera.orthographic_scale")

        if name is not None:
            self.name = name

        self.active = True
        Camera.first = False

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

    @property
    def engine(self):
        """
        Get the render engine used by the camera.

        Returns:
            str: Returns the type of render engine. {"cycles", "eevee"}
        """
        return self._engine

    @engine.setter
    def engine(self, engine):
        """
        Sets the render engine that will be used by this camera.

        Note:
            Direct use is discouraged. Use the quality property to set the render engine.

        Args:
            engine (str): Render engine to use. {"cycles", "eevee"}

        Raises:
            ValueError: If the provided render engine is unknown.
        """
        if engine.lower() not in ["cycles", "eevee"]:
            raise ValueError(f"Unknown render engine: {engine}.")

        self._engine = engine

    @property
    def quality(self):
        """
        Get the quality of the camera.

        Returns:
            str: The quality of the camera.
        """
        return self._quality

    @quality.setter
    def quality(self, quality):
        """
        Set the camera quality to a preset.

        Args:
            quality (str): Name of the quality preset defined in the preset file.

        Raises:
            ValueError: If the provided quality preset is unknown.
        """

        try:
            quality_dict = Preset.get(f"camera.quality_presets.{quality}")
        except KeyError:
            raise ValueError(f"Quality preset {quality} not found in the preset file.")

        self._quality = quality
        self.engine = quality_dict["engine"]
        self._quality_dict = quality_dict

    def _apply_render_settings(render):

        @wraps(render)
        def wrapper(self, *args, quality=None, **kwargs):
            if quality is not None:
                self.quality = quality
            quality_dict = self._quality_dict

            # Delayed import to avoid circular import
            from .lib import (
                get_viewport_engine,
                set_viewport_engine,
                set_background_transparent,
            )

            # Set render engine
            viewport_engine = get_viewport_engine()
            set_viewport_engine(self.engine)

            # Set transparent background
            set_background_transparent(Preset.get("render.transparent_background"))

            # Set output
            bpy.data.scenes["Scene"].render.image_settings.color_depth = str(
                Preset.get("render.color_depth")
            )
            bpy.data.scenes["Scene"].render.image_settings.compression = Preset.get(
                "render.compression"
            )

            # Quality settings
            if bpy.context.scene.render.engine == "CYCLES":
                bpy.data.scenes["Scene"].cycles.use_denoising = quality_dict["denoise"]
                bpy.data.scenes["Scene"].cycles.samples = quality_dict["max_samples"]
                bpy.data.scenes["Scene"].cycles.adaptive_threshold = quality_dict[
                    "noise"
                ]
            elif bpy.context.scene.render.engine == "BLENDER_EEVEE":
                bpy.data.scenes["Scene"].eevee.taa_render_samples = quality_dict[
                    "max_samples"
                ]

            # Render
            render(self, *args, **kwargs)

            # Reset render engine
            set_viewport_engine(viewport_engine)
            set_background_transparent(False)

        return wrapper

    @_apply_render_settings
    def render(self, filename=None, quality=None, show=None):
        """
        Renders the scene form the point of view of the active camera.

        Note:
            Will automatically make this camera the active one.

        Args:
            filename (str, optional): The output filename for the rendered image. Default: None. No file is written.
            quality (str, optional): The quality preset to use for rendering. Default: Preset quality of camera.
            show (bool, optional): Whether to display the render window after rendering. Default: None. Value from the preset configuration will be used.

        Raises:
            ValueError: If the parent directory of the specified filename does not exist.
        """
        if show is None:
            show = Preset.get("render.render_window")
        Camera._set_render_window(show)

        write_still = False  # Write out the result
        if filename is not None:
            filename = Path(filename)
            if not filename.parent.exists():
                raise ValueError(f"Directory {filename.parent} does not exist.")

            bpy.context.scene.render.filepath = str(filename)
            write_still = True

        self.active = True
        if show:
            bpy.ops.render.render("INVOKE_DEFAULT", write_still=write_still)
        else:
            bpy.ops.render.render(write_still=write_still)

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

    @classmethod
    def _set_render_window(cls, show):
        """
        Whether or not to show the rendering.

        Args:
            show (bool): TRUE means a window pop up will show the render result. FALSE means the render will not be displayed. Use FALSE for scripts.
        """
        if show:
            bpy.context.preferences.view.render_display_type = "WINDOW"
        else:
            bpy.context.preferences.view.render_display_type = "NONE"
