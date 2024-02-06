from os.path import isabs
from pathlib import Path

import bpy  # type: ignore

from .meshobject import MeshObject


class Asset(MeshObject):
    """
    Represents a complex pre-made object.

    This class loads a pre-made blender object from a .blend file and
    implements the MeshObject interface.

    To create a loadable asset design our object in blender and save a
    .blend file into the asset_directory. The file name should be an all
    lowercase version of the object name inside Blender.

    :param file: The name of the asset (object) to load.
    :type file: str

    :cvar asset_directory: The directory where the assets are located.
    :vartype asset_directory: Path

    **Example**::
        # loads the object "NanoESCA" from the 'asset_directory / nanoesca.blend' file.
        >>> detector = Asset("NanoESCA")

    """

    asset_directory = Path(__file__).parent / "resources" / "assets"

    def __init__(self, file):
        blender_object = Asset._load_asset(file)
        bpy.context.view_layer.objects.active = blender_object
        super().__init__()

    @classmethod
    def _load_asset(cls, file):
        """
        .. :meta private:

        Loads the asset file into Blender.

        This method appends an object from a specified .blend file into the current Blender scene. The file should
        be located in the predefined asset directory, and its name should be provided without the .blend extension.
        The method assumes that the object's name inside the .blend file matches the file name.

        :param file: The name of the asset file to load, excluding the .blend extension.
        :type file: str

        :returns: The Blender object representing the loaded asset. If the object cannot be found or loaded, None
        is returned.
        :rtype: bpy.types.Object or None
        """
        if isabs(file):
            directory = Path(file) / "Object"
        else:
            directory = Asset.asset_directory / f"{file.lower()}.blend" / "Object"

        bpy.ops.wm.append(
            filepath="//Object/" + file,
            filename=file,
            directory=str(directory),
        )

        return bpy.data.objects.get(file)
