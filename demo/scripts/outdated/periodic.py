from pathlib import Path
from blentom import *

reset()

dir_ = Path(".") / "demo"

periodicity = (5, 9, 6)
atom = Atoms.read(dir_ / "data" / "POSCAR")
atom.periodic(periodicity)
light = Light()
camera = Camera((9, -5, 50), (50, 0, 20))
camera.focuslength = 35
# camera.render(dir_ / "output" / "periodic.png", mode="quality")
