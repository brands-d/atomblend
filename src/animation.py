import bpy

from .preset import Preset


class Animation:
    """
    Represents an animation in Blender. A helper class not meant to be used directly.
    """

    def __init__(self):
        self.interpolation_type = Preset.get("animation.interpolation")
        self.fps = Preset.get("animation.fps")
        self.current_frame = 1

    @property
    def interpolation_type(self):
        """
        The interpolation type used for keyframe animation.

        Returns:
            str: The interpolation type. {'linear'}
        """
        return bpy.context.preferences.edit.keyframe_new_interpolation_type.lower()

    @interpolation_type.setter
    def interpolation_type(self, interpolation_type):
        """
        Sets the interpolation type used for keyframe animation.

        Args:
            interpolation_type (str): The interpolation type to set. {'linear'}

        Raises:
            ValueError: If the interpolation type is invalid.
        """
        try:
            bpy.context.preferences.edit.keyframe_new_interpolation_type = (
                interpolation_type.upper()
            )
        except AttributeError:
            raise ValueError("Invalid interpolation type.")

    @property
    def fps(self):
        """
        The frames per second (FPS) of the animation.

        Returns:
            int: The FPS.
        """
        return bpy.context.scene.render.fps

    @fps.setter
    def fps(self, fps):
        """
        Sets the frames per second (FPS) of the animation.

        Args:
            fps (int): The FPS to set.
        """
        bpy.context.scene.render.fps = fps

    @property
    def initial_frame(self):
        """
        The initial frame of the animation.

        Returns:
            int: The initial frame.
        """
        return bpy.context.scene.frame_start

    @initial_frame.setter
    def initial_frame(self, initial_frame):
        """
        Sets the initial frame of the animation.

        Args:
            initial_frame (int): The initial frame to set.
        """
        bpy.context.scene.frame_start = initial_frame

    @property
    def final_frame(self):
        """
        The final frame of the animation.

        Returns:
            int: The final frame.
        """
        return bpy.context.scene.frame_end

    @final_frame.setter
    def final_frame(self, final_frame):
        """
        Sets the final frame of the animation.

        Args:
            final_frame (int): The final frame to set.
        """
        bpy.context.scene.frame_end = final_frame

    @property
    def current_frame(self):
        """
        The current frame of the animation.

        Returns:
            int: The current frame.
        """
        return bpy.context.scene.frame_current

    @current_frame.setter
    def current_frame(self, current_frame):
        """
        Sets the current frame of the animation.

        Args:
            current_frame (int): The current frame to set.
        """
        bpy.context.scene.frame_current = current_frame
