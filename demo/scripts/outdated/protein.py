from pathlib import Path
from blentom import Atoms, reset

reset()

dir_ = Path(".") / "demo"
atom = Atoms.read(dir_ / "data" / "6y76.cube")  # Slow!
