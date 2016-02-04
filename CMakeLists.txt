project(uranium)

cmake_minimum_required(VERSION 2.8.12)

include(GNUInstallDirs)

find_package(PythonInterp 3.4.0 REQUIRED)

# Tests
add_custom_target(tests)
add_custom_command(TARGET tests POST_BUILD COMMAND "PYTHONPATH=${CMAKE_SOURCE_DIR}" ${PYTHON_EXECUTABLE} ARGS -m pytest -r a --junitxml=${CMAKE_BINARY_DIR}/junit.xml ${CMAKE_SOURCE_DIR})

# # Benchmarks
# add_custom_target(benchmark)
# file(GLOB bench_files tests/benchmarks/*/profile*.py)
# foreach(file ${bench_files})
#     add_custom_command(TARGET benchmark POST_BUILD COMMAND "PYTHONPATH=${CMAKE_SOURCE_DIR}" kernprof ARGS -l -v ${file})
# endforeach()


# Documentation

# Macro needed to list all sub-directory of a directory.
# There is no function in cmake as far as I know.
# Found at: http://stackoverflow.com/a/7788165
MACRO(SUBDIRLIST result curdir)
  FILE(GLOB children RELATIVE ${curdir} ${curdir}/*)
  SET(dirlist "")
  FOREACH(child ${children})
    IF(IS_DIRECTORY ${curdir}/${child})
        LIST(APPEND dirlist ${child})
    ENDIF()
  ENDFOREACH()
  SET(${result} ${dirlist})
ENDMACRO()

find_package(Doxygen)
if(${DOXYGEN_FOUND})
    add_custom_target(doc ${DOXYGEN_EXECUTABLE} ${CMAKE_SOURCE_DIR}/Doxyfile WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endif()

# Extract Strings
add_custom_target(extract-messages ${CMAKE_SOURCE_DIR}/scripts/extract-messages ${CMAKE_SOURCE_DIR} uranium)

# Build Translations
find_package(Gettext)

if(GETTEXT_FOUND)
    # translations target will convert .po files into .mo and .qm as needed.
    # The files are checked for a _qt suffix and if it is found, converted to
    # qm, otherwise they are converted to .po.
    add_custom_target(translations ALL)
    # copy-translations can be used to copy the built translation files from the
    # build directory to the source resources directory. This is mostly a convenience
    # during development, normally you want to simply use the install target to install
    # the files along side the rest of the application.
    add_custom_target(copy-translations)

    SUBDIRLIST(languages ${CMAKE_SOURCE_DIR}/resources/i18n/)
    foreach(lang ${languages})
        file(GLOB po_files ${CMAKE_SOURCE_DIR}/resources/i18n/${lang}/*.po)
        foreach(po_file ${po_files})
            string(REGEX REPLACE ".*/(.*).po" "${CMAKE_BINARY_DIR}/resources/i18n/${lang}/LC_MESSAGES/\\1.mo" mo_file ${po_file})
            add_custom_command(TARGET translations POST_BUILD COMMAND mkdir ARGS -p ${CMAKE_BINARY_DIR}/resources/i18n/${lang}/LC_MESSAGES/ COMMAND ${GETTEXT_MSGFMT_EXECUTABLE} ARGS ${po_file} -o ${mo_file} -f)
        endforeach()
    endforeach()
    install(DIRECTORY ${CMAKE_BINARY_DIR}/resources DESTINATION ${CMAKE_INSTALL_DATADIR}/uranium/)
endif()

if(APPLE OR WIN32)
    install(DIRECTORY UM DESTINATION lib/python${PYTHON_VERSION_MAJOR}.${PYTHON_VERSION_MINOR}/site-packages)
else()
    install(DIRECTORY UM DESTINATION lib/python${PYTHON_VERSION_MAJOR}/dist-packages)
endif()
install(DIRECTORY resources DESTINATION ${CMAKE_INSTALL_DATADIR}/uranium)
install(DIRECTORY plugins DESTINATION lib/uranium)

include(CPackConfig.cmake)
