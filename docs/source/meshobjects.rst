Basic Objects
^^^^^^^^^^^^^
Blentom distingueshes between two types of objects: Objects and MeshObjects. The former is an abstraction of any object in scene and includes objects like lights and cameras. It implements basic functionality like movement and rotation.
MeshObjects inherit the Object interface but also include functionality for scaling and materials. MeshObjects are atoms, bonds and isosurfaces.

.. autoclass:: src.meshobject.Object
   :members:
   :special-members:
   :show-inheritance:


.. autoclass:: src.meshobject.MeshObject
   :members:
   :special-members:
   :show-inheritance: