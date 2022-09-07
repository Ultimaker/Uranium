# Copyright (c) 2022 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

# For MSVC flags, will be ignored on non-Windows OS's and this project in general. Only needed for cura-build-environment.
cmake_policy(SET CMP0091 NEW)
project(uranium NONE)

cmake_minimum_required(VERSION 3.18)

list(APPEND CMAKE_MODULE_PATH ${CMAKE_SOURCE_DIR}/cmake/)

include(GNUInstallDirs)

include(UraniumTranslationTools)

# Extract Strings
add_custom_target(extract-messages ${CMAKE_SOURCE_DIR}/scripts/extract-messages ${CMAKE_SOURCE_DIR} uranium)

# Build Translations
CREATE_TRANSLATION_TARGETS()


install(DIRECTORY UM DESTINATION "${Python_SITELIB_LOCAL}")

install(FILES ${CMAKE_SOURCE_DIR}/cmake/UraniumTranslationTools.cmake
        DESTINATION ${CMAKE_INSTALL_DATADIR}/cmake-${CMAKE_MAJOR_VERSION}.${CMAKE_MINOR_VERSION}/Modules/ )
install(DIRECTORY resources DESTINATION ${CMAKE_INSTALL_DATADIR}/uranium)
