from bpy.props import StringProperty
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper

from .atom import Atoms
from .isosurface import Wavefunction, ChargeDensity


class CubeImport(Operator, ImportHelper):
    """
    Operator class for importing .cube files.
    """

    bl_idname = "import.cube"
    bl_label = "Import .cube"

    filename_ext = ".cube"

    filter_glob: StringProperty(default="*.cube", options={"HIDDEN"}, maxlen=255)

    def execute(self, context):
        """
        Executes the import operation for .cube files.
        Reads the file using the Atoms and Wavefunction classes.
        Returns a dictionary indicating the operation is finished.
        """
        Atoms.read(self.filepath)
        Wavefunction.read(self.filepath)
        return {"FINISHED"}


def menu_func_import_cube(self, *args, **kwargs):
    """
    Menu function for importing .cube files.
    Adds the CubeImport operator to the import menu.
    """
    self.layout.operator(CubeImport.bl_idname, text="Gaussian Cube (.cube)")


class XYZImport(Operator, ImportHelper):
    """
    Operator class for importing .xyz files.
    """

    bl_idname = "import.xyz"
    bl_label = "Import .xyz"

    filename_ext = ".xyz"

    filter_glob: StringProperty(default="*.xyz", options={"HIDDEN"}, maxlen=255)

    def execute(self, context):
        """
        Executes the import operation for .xyz files.
        Reads the file using the Atoms class.
        Returns a dictionary indicating the operation is finished.
        """
        Atoms.read(self.filepath)
        return {"FINISHED"}


def menu_func_import_xyz(self, *args, **kwar):
    """
    Menu function for importing .xyz files.
    Adds the XYZImport operator to the import menu.
    """
    self.layout.operator(XYZImport.bl_idname, text="XYZ (.xyz)")


class POSCARImport(Operator, ImportHelper):
    """
    Operator class for importing POSCAR files.
    """

    bl_idname = "import.poscar"
    bl_label = "Import POSCAR"

    def execute(self, context):
        """
        Executes the import operation for POSCAR files.
        Reads the file using the Atoms class.
        Returns a dictionary indicating the operation is finished.
        """
        Atoms.read(self.filepath)
        return {"FINISHED"}


def menu_func_import_poscar(self, *args, **kwar):
    """
    Menu function for importing POSCAR files.
    Adds the POSCARImport operator to the import menu.
    """
    self.layout.operator(POSCARImport.bl_idname, text="POSCAR (POSCAR)")


class CHGCARImport(Operator, ImportHelper):
    """
    Operator class for importing CHGCAR files.
    """

    bl_idname = "import.chgcar"
    bl_label = "Import CHGCAR"

    def execute(self, context):
        """
        Executes the import operation for CHGCAR files.
        Reads the file using the Atoms and ChargeDensity classes.
        Returns a dictionary indicating the operation is finished.
        """
        Atoms.read(self.filepath)
        ChargeDensity.read(self.filepath)
        return {"FINISHED"}


def menu_func_import_chgcar(self, *args, **kwargs):
    """
    Menu function for importing CHGCAR files.
    Adds the CHGCARImport operator to the import menu.
    """
    self.layout.operator(CHGCARImport.bl_idname, text="CHGCAR/PARCHG")
