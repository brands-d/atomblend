from pathlib import Path
from json import load


class Preset:
    presets_path = Path(__file__).parent / "resources" / "presets.json"

    preset = load(open(presets_path))["default"]

    """
        material:
            style: "standard", "eggshell", "plastic", "metallic", "magnetics"
        atom:
            size: float
        mesh:
            smooth: bool
            viewport_quality: "low", "medium", "high"
            render_quality: "low", "medium", "high"
    """

    @classmethod
    def load(cls, name):
        Preset.preset = load(open(Preset.presets_path))[name]

    @classmethod
    def get(cls, setting):
        group, setting = setting.split(".")
        return Preset.preset[group][setting]

    @classmethod
    def set(cls, setting, value):
        group, setting = setting.split(".")
        Preset.preset[group][setting] = value
