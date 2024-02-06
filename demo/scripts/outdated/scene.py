from pathlib import Path
from blentom import *

reset()

dir_ = Path(".") / "demo"
atom = Atoms.read(dir_ / "data" / "benzene_HOMO-6.cube")
wf = Wavefunction.read(dir_ / "data" / "benzene_HOMO-6.cube")

Light(5)
background = Plane()
background.material = Material("Background", {"Base Color": (0, 0, 0, 1)})

camera = Camera((0, -12, 9), (50, 0, 0))
camera.focuslength = 30
camera.resolution = (1080, 608)

#camera.render(dir_ / "output" / "demo2.png")
