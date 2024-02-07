from pathlib import Path


class Preset:
    preset = {
        "material": {"style": "metallic"},
        "atom": {
            "size": 1,
            "smooth": True,
            "viewport_quality": 1,
            "render_quality": 2,
        },
    }

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

    def __new__(cls, name):
        super().__new__(cls)

        # TODO LOAD PRESET

        return None

    @classmethod
    def get(cls, setting):
        group, setting = setting.split(".")
        return Preset.preset[group][setting]

    @classmethod
    def set(cls, setting, value):
        group, setting = setting.split(".")
        Preset.preset[group][setting] = value
