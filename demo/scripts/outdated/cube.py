from pathlib import Path
from blentom import *

# Delete objects loaded from previous run
reset()
dir_ = Path(".") / "demo"

# Load ase.atoms object from any file type ase.io.read supports
atom = Atoms.read(dir_ / "data" / "benzene_HOMO-6.cube")
# Load the wavefunction from a .cube file
wf = Wavefunction.read(dir_ / "data" / "benzene_HOMO-6.cube")

# Camera object needed for rendering
camera = Camera()
# Use "fast" to set scene, "quality" for final render (much slower)
# camera.render(dir_ / "output" / "cube.png", mode="quality")
