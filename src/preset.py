from pathlib import Path
from json import load


class Preset:
    presets_directory = Path(__file__).parent / "resources" / "presets"

    presets = load(open(presets_directory / "presets.json"))
    presets.update(load(open(presets_directory / "presets_user.json")))
    preset = "default"

    """
        material:
            atoms: "basic", "standard", "eggshell", "plastic", "metallic", "magnetics"
            chargedensity: "basic", "standard", "eggshell", "plastic",
            "metallic", "magnetics"
            bonds: "basic", "standard", "eggshell", "plastic",
            "metallic", "magnetics"
        atom:
            size: float
        mesh:
            smooth: bool
            viewport_quality: "low", "medium", "high"
            render_quality: "low", "medium", "high"
    """

    @classmethod
    def load(cls, name):
        Preset.preset = name
        Preset.presets = load(open(Preset.presets_directory / "presets.json"))
        Preset.presets.update(
            load(open(Preset.presets_directory / "presets_user.json"))
        )

    @classmethod
    def get(cls, setting):
        group, setting = setting.split(".")
        return Preset.presets[Preset.preset][group][setting]

    @classmethod
    def set(cls, setting, value):
        group, setting = setting.split(".")
        Preset.presets[Preset.preset][group][setting] = value
