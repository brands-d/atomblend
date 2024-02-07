from .dependencies import install_dependencies

install_dependencies()

import bpy  # type: ignore
from . import auto_load

from .src import *

bl_info = {
    "name": "blentom",
    "author": "Dominik Brandstetter",
    "email": "dominik.brandstetter@uni-graz.at",
    "license": "MIT",
    "version": (2, 0),
    "blender": (4, 0, 0),
    "description": "Import of common electronic structure files.",
    "doc_url": "https://github.com/brands-d/blentom/tree/main",
    "tracker_url": "https://github.com/brands-d/blentom/issues",
    "category": "Import-Export",
}


def register():
    bpy.utils.register_class(CubeImport)
    bpy.utils.register_class(XYZImport)
    bpy.utils.register_class(POSCARImport)
    bpy.utils.register_class(CHGCARImport)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_cube)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_xyz)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_poscar)
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_chgcar)
    pass


def unregister():
    bpy.utils.unregister_class(CubeImport)
    bpy.utils.unregister_class(XYZImport)
    bpy.utils.unregister_class(POSCARImport)
    bpy.utils.unregister_class(CHGCARImport)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_cube)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_xyz)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_poscar)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_chgcar)
    pass


if __name__ == "__main__":
    auto_load.init()
