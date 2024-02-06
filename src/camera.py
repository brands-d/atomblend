import bpy  # type: ignore

from .object import Object


class Camera(Object):
    _blender_object = None

    def __init__(self, position=(0, 0, 10), rotation=(0, 0, 0)):
        if self.blender_object is None:
            self.blender_object = bpy.context.scene.camera

        self.position = position
        self.rotation = rotation
        self.resolution = (1080, 1080)

    @property
    def blender_object(self):
        return Camera._blender_object

    @blender_object.setter
    def blender_object(self, blender_object):
        Camera._blender_object = blender_object

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
        return self._blender_object.lens

    @focuslength.setter
    def focuslength(self, focuslength):
        self._blender_object.lens = focuslength
