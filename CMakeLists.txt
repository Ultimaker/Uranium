project(uranium NONE)

cmake_minimum_required(VERSION 2.8.12)

include(GNUInstallDirs)

option(CURA_BINARY_DATA_DIRECTORY "Directory to the cura-binary-data repository")

if(NOT CURA_BINARY_DATA_DIRECTORY AND NOT DEFINED $ENV{CURA_BINARY_DATA_DIRECTORY})
    message(STATUS "Using CURA_BINARY_DATA_DIRECTORY from set of environment variables...")
    SET(CURA_BINARY_DATA_DIRECTORY $ENV{CURA_BINARY_DATA_DIRECTORY})
endif()

find_package(PythonInterp 3.4.0 REQUIRED)

# Checks using pylint
# Note that we use exit 0 here to not mark the build as a failure on check failure
# In addition, the specified pylint configuration uses the spellchecker plugin. This required python-enchant to be installed.
add_custom_target(check)
add_custom_command(TARGET check POST_BUILD COMMAND "PYTHONPATH=${CMAKE_SOURCE_DIR}" ${PYTHON_EXECUTABLE} -m pylint --rcfile=${CMAKE_SOURCE_DIR}/pylint.cfg UM --msg-template=\"{path}:{line}: [{msg_id}({symbol}), {obj}] {msg}\" > ${CMAKE_BINARY_DIR}/pylint.log || exit 0 WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})

# Tests
# Note that we use exit 0 here to not mark the build as a failure on test failure
add_custom_target(tests)
add_custom_command(TARGET tests POST_BUILD COMMAND "LANG=C" "PYTHONPATH=${CMAKE_SOURCE_DIR}" ${PYTHON_EXECUTABLE} -m pytest -r a --junitxml=${CMAKE_BINARY_DIR}/junit.xml ${CMAKE_SOURCE_DIR} || exit 0)

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
        STRING(REPLACE "/" "" child ${child})
        LIST(APPEND dirlist ${child})
    ENDIF()
  ENDFOREACH()
  SET(${result} ${dirlist})
ENDMACRO()

MACRO(TARGETS_FOR_PO_FILES language)
    if(DEFINED GETTEXT_MSGINIT_EXECUTABLE)
        message(STATUS "Creating target i18n-create-po-${language}")
        add_custom_target(i18n-create-po-${language})
        add_dependencies(i18n-create-po i18n-create-po-${language})
    endif()
    message(STATUS "Creating target i18n-update-po-${language}")
    add_custom_target(i18n-update-po-${language})
    add_dependencies(i18n-update-po i18n-update-po-${language})
    foreach(pot_file ${pot_files})
        string(REGEX REPLACE ".*/(.*).pot" "${CMAKE_SOURCE_DIR}/resources/i18n/${language}/\\1.po" po_file ${pot_file})
        if(DEFINED GETTEXT_MSGINIT_EXECUTABLE)
            add_custom_command(TARGET i18n-create-po-${language} POST_BUILD
                               COMMAND ${GETTEXT_MSGINIT_EXECUTABLE} ARGS --no-wrap --no-translator -l ${language} -i ${pot_file} -o ${po_file})
        endif()
        add_custom_command(TARGET i18n-update-po-${language} POST_BUILD
                           COMMAND ${GETTEXT_MSGMERGE_EXECUTABLE} ARGS --no-wrap -o ${po_file} ${po_file} ${pot_file})
    endforeach()
ENDMACRO()

MACRO(TARGETS_FOR_MO_FILES language)
    message(STATUS "Creating target i18n-create-mo-${language}")
    add_custom_target(i18n-create-mo-${language})
    add_dependencies(i18n-create-mo i18n-create-mo-${language})
    if(TARGET i18n-copy-mo)
        message(STATUS "Creating target i18n-copy-mo-${language}")
        add_custom_target(i18n-copy-mo-${language})
        add_dependencies(i18n-copy-mo i18n-copy-mo-${language})
    endif()
    file(GLOB po_files ${CMAKE_SOURCE_DIR}/resources/i18n/${language}/*.po)
    foreach(po_file ${po_files})
        string(REGEX REPLACE ".*/(.*).po" "${CMAKE_BINARY_DIR}/resources/i18n/${language}/LC_MESSAGES/\\1.mo" mo_file ${po_file})
        add_custom_command(TARGET i18n-create-mo-${language} POST_BUILD
                           COMMAND mkdir ARGS -p ${CMAKE_BINARY_DIR}/resources/i18n/${language}/LC_MESSAGES/
                           COMMAND ${GETTEXT_MSGFMT_EXECUTABLE} ARGS ${po_file} -o ${mo_file} -f)
        if(TARGET i18n-copy-mo-${language})
             string(REGEX REPLACE ".*/(.*).po" "${CURA_BINARY_DATA_DIRECTORY}/${PROJECT_NAME}/resources/i18n/${language}/LC_MESSAGES/\\1.mo" mo_file_binary_copy ${po_file})
             add_custom_command(TARGET i18n-copy-mo-${language} POST_BUILD
                                COMMAND mkdir ARGS -p ${CURA_BINARY_DATA_DIRECTORY}/resources/i18n/${language}/LC_MESSAGES/
                                COMMAND cp ARGS -fv ${mo_file} ${mo_file_binary_copy})
             add_dependencies(i18n-copy-mo-${language} i18n-create-mo-${language})
        endif()
    endforeach()
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
    if(DEFINED GETTEXT_MSGINIT_EXECUTABLE)
        message(STATUS "Creating target i18n-create-po")
        add_custom_target(i18n-create-po)
    else()
        message(WARNING "GETTEXT_MSGINIT_EXECUTABLE is undefined!\nSkipping to create i18n-create-po* targets...")
    endif()
    if(CURA_BINARY_DATA_DIRECTORY)
        if(EXISTS ${CURA_BINARY_DATA_DIRECTORY})
            message(STATUS "CURA_BINARY_DATA_DIRECTORY: ${CURA_BINARY_DATA_DIRECTORY}")
            message(STATUS "Creating target i18n-copy-mo")
            add_custom_target(i18n-copy-mo)
        else()
            message(WARNING "CURA_BINARY_DATA_DIRECTORY does not exist! (${CURA_BINARY_DATA_DIRECTORY})")
        endif()
    else()
        message(WARNING "CURA_BINARY_DATA_DIRECTORY is not set!")
    endif()
    message(STATUS "Creating target i18n-update-po")
    add_custom_target(i18n-update-po)
    message(STATUS "Creating target i18n-update-mo")
    add_custom_target(i18n-create-mo ALL)

    SUBDIRLIST(languages ${CMAKE_SOURCE_DIR}/resources/i18n/)
    file(GLOB pot_files ${CMAKE_SOURCE_DIR}/resources/i18n/*.pot)
    foreach(language ${languages})
        TARGETS_FOR_PO_FILES(${language})
        TARGETS_FOR_MO_FILES(${language})
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
