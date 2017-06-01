##
# Copyright (c) 2011 Aldebaran Robotics. All Rights Reserved.

cmake_minimum_required(VERSION 2.6.4 FATAL_ERROR)
# Give a name to the project.
project(setposture)
# This include enable you to use qibuild framework
find_package(qibuild)

# Create an executable named sayhelloworld,
# with the source file : sayhelloworld.cpp
qi_create_bin(setposture setposture.cpp)

# Tell CMake that sayhelloworld depends on ALCOMMON and ALPROXIES
# This will set the libraries to link sayhelloworld with,
# the include paths, and so on
qi_use_lib(setposture ALCOMMON ALPROXIES)
