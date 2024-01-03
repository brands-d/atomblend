import bpy  # type: ignore

from blentom.base import BlenderObject  # type: ignore


class Camera(BlenderObject):
    instance = None
    blender_object = None

    def __new__(cls, position=(0, 0, 20), rotation=(0, 0, 0)):
        if cls.instance is None:
            cls.instance = super(Camera, cls).__new__(cls)
            cls.blender_object = bpy.context.scene.camera
            cls.instance.position = position
            cls.instance.rotation = rotation
            cls.instance.resolution = (1080, 1080)
        return cls.instance

    @property
    def resolution(self):
        return (
            bpy.context.scene.render.resolution_x,
            bpy.context.scene.render.resolution_y,
        )

    @resolution.setter
    def resolution(self, resolution):
        bpy.context.scene.render.resolution_x = resolution[0]
        bpy.context.scene.render.resolution_y = resolution[1]

    @property
    def focuslength(self):
        return bpy.data.cameras["Camera"].lens

    @focuslength.setter
    def focuslength(self, focuslength):
        bpy.data.cameras["Camera"].lens = focuslength

    def render(self, filepath=None):
        engine = bpy.context.scene.render.engine
        bpy.context.scene.render.engine = "CYCLES"
        if filepath is not None:
            bpy.context.scene.render.filepath = str(filepath)
            bpy.ops.render.render(write_still=True)
        else:
            bpy.ops.render.render()
        bpy.context.scene.render.engine = engine
