qi_create_lib(nav_global_library
  SHARED
  distance_map.cpp distance_map.h
  defs.h
  )
qi_use_lib(nav_global_library 
  OPENCV2_CORE
  EIGEN3
  )
qi_stage_lib(nav_global_library)