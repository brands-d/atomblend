from os.path import isabs
from pathlib import Path

import bpy  # type: ignore

from .meshobject import MeshObject


class Asset(MeshObject):
    """
    Represents a complex pre-made object.

    This class loads a pre-made blender object from a .blend file and
    implements the MeshObject interface.

    To create a loadable asset, design your object in Blender and save the
    .blend file into the `asset_directory`. The file name should be the lowercase
    version of the object name inside Blender.

    Attributes:
        asset_directory (Path): The directory where the assets are located.

    Args:
        file (str): The name of the asset (object) to load.

    Examples:
        >>> detector = Asset("NanoESCA")
        This will load the object "NanoESCA" from the 'asset_directory/nanoesca.blend' file.
    """

    asset_directory = Path(__file__).parent / "resources" / "assets"

    def __init__(self, file):
        blender_object = Asset._load_asset(file)
        bpy.context.view_layer.objects.active = blender_object
        super().__init__()

    @classmethod
    def _load_asset(cls, file):
        """
        Loads the asset file into Blender as a private method.

        This method appends an object from a specified .blend file into the current Blender scene. The file should
        be located in the predefined asset directory, and its name should be provided without the .blend extension.
        It assumes that the object's name inside the .blend file matches the file name.

        Args:
            file (str): The name of the asset file to load, excluding the .blend extension.

        Returns:
            bpy.types.Object or None: The Blender object representing the loaded asset. Returns None if the object
            cannot be found or loaded.
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
