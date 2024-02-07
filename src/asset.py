from os.path import isabs
from pathlib import Path

import bpy  # type: ignore

from .meshobject import MeshObject


class Asset(MeshObject):
    """
    Imports a (complex) pre-made object (e.g. detectors, photons, etc.) from a
    .blend file into the scene.

    Assets are loaded from the `asset_directory` and added into the current
    scene. To create a loadable asset, design your object in Blender and save the .blend file into the `asset_directory`.

    Note:
        Currently only one object per .blend file is supported and it is
        assumed that the filename is an all lowercase version of the objects
        name inside the .blend file.

    Attributes:
        asset_directory (Path): The directory where the assets are located.
            (`src/resources/assets`)

    Args:
        file (str): The name of the asset (object) to load.

    Examples:
        This will load the object "NanoESCA" from the `asset_directory/nanoesca.blend` file.
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
        PRIVATE: Tries to load the asset file into Blender.

        Args:
            file (str): The name of the asset (object) to load.

        Returns:
            bpy.types.Object or None: The Blender object representing the
            loaded asset. Returns None if the object cannot be found or loaded.
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
