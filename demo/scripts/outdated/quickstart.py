from blentom import *

atom = Atoms.read("demo/data/PTCDA.xyz")
Light()
Camera().render("demo/output/quickstart.png")
