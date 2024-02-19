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

         * subsubgroupd (if any)

            * property: (type), {list of options}

Presets:
   * atoms 
 
      * size: (int)
      * material: (str), {basic, standard, eggshell, plastic, metallic, magnetics}
      * quality:

         * segment: (int)
         * rings: (int)
         * smooth: (bool)
         * viewport_quality: (int)
         * render_quality: (int)
      
      * *element name*: (str), {C, H, ...}
         
         * Specify global atoms properties here for specific elements
      
   * camera
      
      * quality (str): {one of the quality_presets}
      * resolution: ([int, int])
      * focuslength: (float)
      * orthographic_scale: (float)
      * lens: (str), {"perspective", "orthographic", "panoramic"}
      * quality_presets

         * *name_of_preset*

            * engine: (str), {cycles, eevee}
            * max_samples: (int)
            * noise: (float), if cycles
            * denoise: (bool), if cycles

   * light

         * default_type: (str), {point, sun, spot, area}
         * sun

            * color: ([float, float, float])
            * energy: (float)
            * angle: (float)
            * shadows: (bool)
         
         * point
          
            * color: ([float, float, float])
            * energy: (float)
            * radius: (float)
            * shadows: (bool)

   * blender

      * viewport_engine: (str), {cycles, eevee}
      * wireframe: (bool)
   
   * animation

      * interpolation: (str), {linear}
      * interpolated_frames: (int)
      * fps: (int)

   * misc

      * render_window: (bool)

Preset Class
""""""""""""
.. autoclass:: src.preset.Preset
   :members:
   :special-members:
   :exclude-members: __weakref__