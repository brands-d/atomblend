from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from .atom import Atoms
from .isosurface import Wavefunction, ChargeDensity


class CubeImport(Operator, ImportHelper):
    bl_idname = "import.cube"
    bl_label = "Import .cube"

    filename_ext = ".cube"

    filter_glob: StringProperty(default="*.cube", options={"HIDDEN"}, maxlen=255)

    def execute(self, context):
        Atoms.read(self.filepath)
        Wavefunction.read(self.filepath)
        return {"FINISHED"}


def menu_func_import_cube(self, *args, **kwargs):
    self.layout.operator(CubeImport.bl_idname, text="Gaussian Cube (.cube)")


class XYZImport(Operator, ImportHelper):
    bl_idname = "import.xyz"
    bl_label = "Import .xyz"

    filename_ext = ".xyz"

    filter_glob: StringProperty(default="*.xyz", options={"HIDDEN"}, maxlen=255)

    def execute(self, context):
        Atoms.read(self.filepath)
        return {"FINISHED"}


def menu_func_import_xyz(self, *args, **kwar):
    self.layout.operator(XYZImport.bl_idname, text="XYZ (.xyz)")


class POSCARImport(Operator, ImportHelper):
    bl_idname = "import.poscar"
    bl_label = "Import POSCAR"

    def execute(self, context):
        Atoms.read(self.filepath)
        return {"FINISHED"}


def menu_func_import_poscar(self, *args, **kwar):
    self.layout.operator(POSCARImport.bl_idname, text="POSCAR (POSCAR)")


class CHGCARImport(Operator, ImportHelper):
    bl_idname = "import.chgcar"
    bl_label = "Import CHGCAR"

    def execute(self, context):
        Atoms.read(self.filepath)
        ChargeDensity.read(self.filepath)
        return {"FINISHED"}


def menu_func_import_chgcar(self, *args, **kwargs):
    self.layout.operator(CHGCARImport.bl_idname, text="CHGCAR/PARCHG")
