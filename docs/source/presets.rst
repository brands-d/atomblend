Presets
^^^^^^^

Presets are a collection of pre-defined settings to simplify the rendering process. Think rcParams from matplotlib. Base settings are defined in the default preset file. Do not edit it as during an update your changes will be overwritten. Instead change the settings you'd like to change or define completely new presets in the presets_user file. Any property not set there will be taken from the default preset from the default file.

Location for preset files
"""""""""""""""""""""""""
   * **default**: ``blentom/src/resources/presets/presets.json``
   * **user**: ``blentom/src/resources/presets/presets_user.json``

Available presets
"""""""""""""""""
   * default

Available properties
""""""""""""""""""""
Notation:
   * *group* (italics: replace name with option*)

      
      * subgroup (if any)

         * property: (type), {list of options}

Presets:
   * atoms

      * *element name*: (str), {carbon, hydrogen, ...}
 
         * size: (int)
         * material: (str), {basic, standard, eggshell, plastic, metallic, magnetics}
         * smooth: (bool)
         * viewport_quality: (int)
         * render_quality: (int)
      
   * camera
      
      * render_engine: (str), {cycles, eevee}
      * resolution: ([int, int])
      * focuslength: (float)
      * orthographic_scale: (float)
      * lens: (str), {"perspective", "orthographic", "panoramic"}

   * blender

      * viewport_engine: (str), {cycles, eevee}
      * wireframe: (bool)

.. autoclass:: src.preset.Preset
   :members:
   :special-members:
   :exclude-members: __weakref__