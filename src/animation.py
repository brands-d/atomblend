def set_frame_range(start, end):
    """
    Sets the frame range of the Blender scene.

    Parameters:
    - start (int): The start frame number.
    - end (int): The end frame number.
    """
    bpy.context.scene.frame_start = start
    bpy.context.scene.frame_end = end


def get_frame_range():
    """
    Gets the frame range of the Blender scene.

    Returns:
    - tuple: The start and end frame numbers.
    """
    return bpy.context.scene.frame_start, bpy.context.scene.frame_end


def set_frame(frame):
    """
    Sets the frame of the Blender scene.

    Parameters:
    - frame (int): The frame number to set.
    """
    bpy.context.scene.frame_set(frame)


def get_frame():
    """
    Gets the frame of the Blender scene.

    Returns:
    - int: The current frame number.
    """
    return bpy.context.scene.frame_current
