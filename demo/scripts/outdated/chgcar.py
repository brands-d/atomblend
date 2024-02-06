from pathlib import Path
from blentom import *

reset()


dir_ = Path(".") / "demo"

atom = Atoms.read(dir_ / "data" / "CHGCAR")
adensity = ChargeDensity.read(dir_ / "data" / "CHGCAR", level=0.45)