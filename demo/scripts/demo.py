#exec(compile(open("/Users/dominik/Desktop/blentom/demo/scripts/demo.py").read(), "/Users/dominik/Desktop/blentom/demo/scripts/test.py", "exec"))

from blentom import *
from ase import Atoms as AseAtoms

reset()

"""
# Atom
# new atoms for given element. 
# Uses default radius and material if possible.
C = Atom("Ni")  # from string
C2 = Atom.ase(AseAtoms("C"))  # from ase

all_atoms = Atom.get("all")
all_carbon_atoms = Atom.get("C")
# Use anonymous functions as powerful filters
all_atoms_below_z0 = Atom.get(lambda atom: atom.location[2] < 0)
all_atoms_with_scale = Atom.get(lambda atom: atom.scale[0] == 1.4)

#C.delete()  # deletes blender object
C2.delete()
"""

"""
# Atoms
O = Atom("O")
H = Atom("H")
H.position = (0.5,0.4,0) # .location is identical
H2O = O + H   # creates new Atoms object (collection of atoms)
H2O.name = "Water"
H = Atom("H")
H.move((-0.5,0.4,0))
H2O += H
# manual bond creation Bond(H, O)
H2O.create_bonds()  # creates bonds; use periodic=False if you don't want bonds across unitcell
"""

"""
#ch4 = AseAtoms("CH4")
#atoms = Atoms.ase(ch4) # move atoms before otherwise bond formation breaks
atoms = Atoms.read("/Users/dominik/Desktop/blentom/demo/data/benzene_HOMO-6.cube")
atoms.name = "Benzene"
atoms.unit_cell
atoms.repeat((1, 0, 0))  # repeats atoms once in x direction as collection instance
atoms.copies_collection  # unit cell repetitions
atoms.atoms  # all atoms in the collection
atoms.bonds  # all bonds in the collection
atoms.get("all")  # similar filter as Atom.get but restricted to Atoms objects
"""

"""
# Basic Object stuff
H = Atom("H")
H.name = "Josef" # name in UI
H.blender_object # reference to blender object
H.scale = 1.2 # multiplicative; only for mesh like objects
H.scale = 1.2
H.move((1,0,0)) # translation
H.position = (1,0,0) # move to given position, .location identical
H.rotation = (30,0,0) # Euler angle like UI, set rotation to fixed value
H.make_active()
H.rotate((30,0,0), origin="local") # rotate object around one point; local == object itself, 3D cursor or world == (0,0,0), or specific point (1,2,3)
"""

"""
atoms = Atom("O")+Atom("H")+Atom("H")
atoms.name = "H20"
atoms.atoms[1].move((0.5,0.5,0))
atoms.atoms[2].move((-0.5,0.5,0))
atoms.create_bonds()
atoms.rotate((0,0,75), atoms.atoms[1])
"""

"""
# Collections
col = Collection("Water")
col += Atom("H")
C= Atom("C")
col.add(C)
#col.remove(Atom.get("H")[0]) # also -
col.dissolve()


col = Collection("CH")
col.add((C,Atom("H")))
C.move((0,1,1))
col.origin = C # for location and rotate(). Can be (x,y,z), "world", "cursor", an Object or center of the collection objects
#col.location = (0,0,0)
"""

"""
# Assets
detector = Asset("NanoESCA") # loads blender object from file at correct location and name
"""

"""
# Material
mat = Material("O") # tries to load nice default material, otherwise old material. If already material is loaded use this one
O = Atom("H")
O.material = Material("O")
substrate = Atom.get(lambda atom: atom.location[2] < 0)
substrate.material = Material("Substrate")
# tools for creating materials are coming, default Materials are not designed yet
"""


"""
#Isosurfaces (all types are under this new umbrella)
#Isosurfaces.read()
# but use custom classes for simpler access
cubefile = Wavefunction.read("/Users/dominik/Desktop/blentom/demo/data/benzene_HOMO-6.cube")
cubefile.name = "Benzene"
cubefile.level= 0.02
"""


Preset.set("atom.viewport_quality", 0)
Preset.set("atom.render_quality", 3)
Preset.set("atom.size", 0.8)
Preset.set("atom.smooth", False)
Atom("H")
