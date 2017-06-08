qi_create_lib(localizer_library  
  SHARED
  localization_filter.cpp localization_filter.h
  )
qi_use_lib(localizer_library 
  nav_global_library
  OPENCV2_CORE
  OPENCV2_IMGPROC
  )
qi_stage_lib(localizer_library)

qi_create_lib(naoqi_localizer_library  
  SHARED
  naoqi_localizer.cpp naoqi_localizer.h
  )
qi_use_lib(naoqi_localizer_library 
  localizer_library
  yaml_parser_library
  ALCOMMON 
  ALPROXIES
  OPENCV2_CORE
  OPENCV2_HIGHGUI
  )
qi_stage_lib(naoqi_localizer_library)


qi_create_bin(pepper_localizer pepper_localizer.cpp)
qi_use_lib(pepper_localizer ALCOMMON ALPROXIES naoqi_localizer_library)

