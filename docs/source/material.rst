Material
^^^^^^^^

Abstraction of a Blender material. While basic methods to create and edit materials exist, the preferred way is to create materials of your liking inside the user materials file and load them. 


.. warning::

   If you create a material in the materials_user.blend file make sure to click the |shield| icon next to the material name. This will prevent the material from being deleted when the file is closed.
   It should like this: |shield_clicked|.

.. |shield| image:: fake_user.png
.. |shield_clicked| image:: fake_user_clicked.png

.. warning::

   The user materials file is not included in the repository. You will have to create it yourself. The default materials file is included in the repository and should not be edited. Any material you create in the default file will be deleted when updating blentom.

Location for materials files
""""""""""""""""""""""""""""

   * **default**: ``blentom/src/resources/materials/materials.blend``
   * **user**: ``blentom/src/resources/presets/materials_user.blend``


Available materials
""""""""""""""""""""
   
   * Elements
      For elements the naming convention is "Fullname - type". Example: "Carbon - standard".
   
   * Types
      * standard
      * basic
      * metallic
      * eggshell
      * magnetics
      * plastic

Material Class
"""""""""""""""

.. autoclass:: src.material.Material
   :show-inheritance:
   :members:
   :special-members:
   :exclude-members: __weakref__