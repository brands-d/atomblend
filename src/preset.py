from pathlib import Path
from json import load


class Preset:
    presets_directory = Path(__file__).parent / "resources" / "presets"

    preset = load(open(presets_directory / "presets.json"))["default"]
    preset.update(load(open(presets_directory / "presets_user.json")))

    """
        material:
            style: "basic", "standard", "eggshell", "plastic", "metallic", "magnetics"
        atom:
            size: float
        mesh:
            smooth: bool
            viewport_quality: "low", "medium", "high"
            render_quality: "low", "medium", "high"
    """

    @classmethod
    def load(cls, name):
        Preset.preset = load(open(Preset.presets_directory))[name]

    @classmethod
    def get(cls, setting):
        group, setting = setting.split(".")
        return Preset.preset[group][setting]

    @classmethod
    def set(cls, setting, value):
        group, setting = setting.split(".")
        Preset.preset[group][setting] = value
