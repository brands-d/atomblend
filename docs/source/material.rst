Material
^^^^^^^^

Abstraction of a Blender material. While basic methods to create and edit materials exist, the preferred way is to create materials of your liking inside the ``src/resources/materials/materials_user.blend`` file and load them. 

.. warning::

   If you create a material in the materials_user.blend file make sure to click the |shield| icon next to the material name. This will prevent the material from being deleted when the file is closed.
   It should like this: |shield_clicked|.

.. |shield| image:: fake_user.png
.. |shield_clicked| image:: fake_user_clicked.png

.. autoclass:: src.material.Material
   :show-inheritance:
   :members:
   :special-members:
   :exclude-members: __weakref__