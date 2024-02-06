from pathlib import Path
from blentom import *

reset()

dir_ = Path(".") / "demo"
atom = Atoms.read(dir_ / "data" / "benzene_HOMO-6.cube")
wf = Wavefunction.read(dir_ / "data" / "benzene_HOMO-6.cube")

Light(energy=3)
camera = Camera((0, -10, 9), (53, 0, 0))
camera.focuslength = 35

positive = Material(
    "Positive Wavefunction",
    {
        "Base Color": (1, 0, 0, 1),
        "Alpha": 0.6,
        "Emission Color": (1, 0, 0, 1),
        "Emission Strength": 2,
        "Metallic": 0.8,
        "Sheen Weight": 0.8,
    },
)
wf.positive.material = positive.copy()
negative = positive.update({"Base Color": (0, 0, 1, 1), "Emission Color": (0, 0, 1, 1)})
wf.negative.material = negative

bg_material = Material(
    "Background",
    {
        "Base Color": (0, 0, 0, 0),
        "Roughness": 0.2,
        "Metallic": 0,
        "Specular IOR Level": 1,
        "Specular Tint": (1, 0, 0, 1),
    },
)
background = Plane(location=(0, 0, -2.5), material=bg_material)
background.rotation = (18, 0, 0)
bg_material = bg_material.copy()
bg_material.update({"Specular Tint": (0, 0, 1, 1)})
background2 = Plane(location=(-5, 6, -2), material=bg_material)
background2.rotation = (120, -15, 0)

# camera.render(dir_ / "output" / "demo.png")
