import logging
from json import dump as jdump
from json import load as jload
from pathlib import Path


class Preset:
    """
    A class representing a preset configuration for Blender. This includes but
    is not limited to size of atoms objects, renderer settings and lighting.

    Attributes:
        preset (str): The currently selected preset.
        presets_directory (Path): The directory where the preset files are located.
        presets_file (Path): The file with the default presets.
        presets_user_file (Path): The file containing the user presets.
        presets (dict): A dictionary containing loaded presets.
    """

    preset = ""
    presets = {}
    presets_directory = Path(__file__).parent / "resources" / "presets"
    presets_file = presets_directory / "presets.json"
    presets_user_file = presets_directory / "presets_user.json"

    @classmethod
    def load(cls, name):
        """
        Loads a preset configuration by name.

        Args:
            name (str): The name of the preset to load.
        """
        Preset._reload_presets()
        Preset.preset = name

    @classmethod
    def get(cls, setting, preset=None):
        """
        Retrieves the value of a specific setting from a preset.

        Args:
            setting (str): The setting to retrieve, in the format "group.[subgroup.]property".
            preset (str | None): The preset from which the property should be returned. Default: Currently loaded preset.

        Returns:
            The value of the specified property.

        Examples:
            >>> # Returns the preset material (name) for Carbon atoms
            >>> Preset.get("atoms.carbon.material")
            >>> # Returns the preset size of all bonds
            >>> Preset.get("bonds.size")
            >>> # Returns the resolution of the "default" preset
            >>> Preset.get("camera.resolution", preset="default")
        """
        preset = Preset.preset if preset is None else preset
        Preset._reload_presets()

        setting = setting.split(".")
        if len(setting) == 2:
            # No subgroup
            group, property = setting
            return Preset.presets[preset][group][property]
        elif len(setting) == 3:
            # Subgroup
            group, subgroup, property = setting
            return Preset.presets[preset][group][subgroup][property]
        else:
            raise ValueError("Wrong setting format. Use: group.[subgroup.]property")

    @classmethod
    def set(cls, setting, value, preset=None):
        """
        Sets the value of a specific property in a preset. Edits the user preset file!

        Args:
            setting (str): The property to set, in the format "group.[subgroup.]property".
            value (any): The value to set for the specified property.
            preset (str | None): The preset for which the property should be set. Default: Currently loaded preset.

        Examples:
            >>> # Sets the size for carbon atoms in the "default" preset
            >>> Preset.set("atoms.carbon.size", 1.2, preset="default")
        """
        preset = Preset.preset if preset is None else preset
        user_preset = Preset._read_user_preset_file()

        setting = setting.split(".")
        if len(setting) == 2:
            # No subgroup
            group, property = setting
            user_preset.update({preset: {group: {property: value}}})
        elif len(setting) == 3:
            # Subgroup
            group, subgroup, property = setting
            user_preset.update({preset: {group: {subgroup: {property: value}}}})
        else:
            raise ValueError("Wrong setting format. Use: group.[subgroup.]property")

        jdump(user_preset, open(Preset.presets_user_file, "w"))

    @classmethod
    def _reload_presets(cls):
        """
        Reloads the presets files.
        """
        # Load default presets
        cls.presets = Preset._read_default_preset_file()
        # Update with user presets
        cls.presets.update(Preset._read_user_preset_file())

    @classmethod
    def _read_default_preset_file(cls):
        """
        Reads the default preset file and returns its contents.

        Returns:
            dict: Dictionary containing the contents of the preset file.
        """
        return jload(open(Preset.presets_file))

    @classmethod
    def _read_user_preset_file(cls):
        """
        Reads the user preset file and returns its contents as a dictionary.

        If the file is not found, an empty file is generated and an empty dictionary is returned.

        Returns:
            dict: Dictionary containing the contents of the user preset file.
        """
        try:
            return jload(open(Preset.presets_user_file))
        except FileNotFoundError:
            logging.warning(
                f"File {Preset.presets_user_file} not found. Generate empty one."
            )
            open(Preset.presets_user_file, "w").write("{}")
            return {}


Preset.load("default")
