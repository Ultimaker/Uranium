# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

project(uranium NONE)

cmake_minimum_required(VERSION 3.18)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/)

include(GNUInstallDirs)

if(NOT DEFINED Python_VERSION)
    set(Python_VERSION
            3.10
            CACHE STRING "Python Version" FORCE)
    message(STATUS "Setting Python version to ${Python_VERSION}. Set Python_VERSION if you want to compile against an other version.")
endif()
if(APPLE)
    set(Python_FIND_FRAMEWORK NEVER)
endif()
find_package(Python ${Python_VERSION} EXACT REQUIRED COMPONENTS Interpreter)
message(STATUS "Linking and building ${project_name} against Python ${Python_VERSION}")
if(NOT DEFINED Python_SITELIB_LOCAL)
    set(Python_SITELIB_LOCAL
            "${Python_SITELIB}"
            CACHE PATH "Local alternative site-package location to install Uranium" FORCE)
endif()

include(UraniumTranslationTools)

# Checks using pylint
# Note that we use exit 0 here to not mark the build as a failure on check failure
# In addition, the specified pylint configuration uses the spellchecker plugin. This required python-enchant to be installed.
add_custom_target(check)
add_custom_command(TARGET check POST_BUILD COMMAND "PYTHONPATH=${CMAKE_SOURCE_DIR}" ${Python_EXECUTABLE} -m pylint --rcfile=${CMAKE_SOURCE_DIR}/pylint.cfg UM --msg-template=\"{path}:{line}: [{msg_id}({symbol}) , {obj}] {msg}\" > ${CMAKE_BINARY_DIR}/pylint.log || exit 0 WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

# Check using Mypy
add_custom_target(typecheck)
add_custom_command(TARGET typecheck POST_BUILD COMMAND ${Python_EXECUTABLE} run_mypy.py WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

# Tests
include(UraniumTests)


# Documentation
find_package(Doxygen)
if(${DOXYGEN_FOUND})
    add_custom_target(doc ${DOXYGEN_EXECUTABLE} ${CMAKE_SOURCE_DIR}/Doxyfile WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endif()

# Extract Strings
add_custom_target(extract-messages ${CMAKE_SOURCE_DIR}/scripts/extract-messages ${CMAKE_SOURCE_DIR} uranium)

# Build Translations
CREATE_TRANSLATION_TARGETS()


install(DIRECTORY UM DESTINATION "${Python_SITELIB_LOCAL}")

install(FILES ${CMAKE_SOURCE_DIR}/cmake/UraniumTranslationTools.cmake
        DESTINATION ${CMAKE_INSTALL_DATADIR}/cmake-${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}/Modules/ )
install(DIRECTORY resources DESTINATION ${CMAKE_INSTALL_DATADIR}/uranium)

# Detect plugins to install
include(UraniumPluginInstall)

include(CPackConfig.cmake)
