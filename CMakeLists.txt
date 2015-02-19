project(uranium)

cmake_minimum_required(VERSION 2.8.12)

find_package(PythonInterp REQUIRED)

# Tests
add_custom_target(tests)
file(GLOB test_files tests/*/Test*.py)
foreach(file ${test_files})
    add_custom_command(TARGET tests POST_BUILD COMMAND "PYTHONPATH=${CMAKE_SOURCE_DIR}" ${PYTHON_EXECUTABLE} ARGS ${file})
endforeach()

# Benchmarks
add_custom_target(benchmark)
file(GLOB bench_files tests/benchmarks/*/profile*.py)
foreach(file ${bench_files})
    add_custom_command(TARGET benchmark POST_BUILD COMMAND "PYTHONPATH=${CMAKE_SOURCE_DIR}" kernprof ARGS -l -v ${file})
endforeach()

# Documentation
find_package(Doxygen)
if(${DOXYGEN_FOUND})
    add_custom_target(doc ${DOXYGEN_EXECUTABLE} ${CMAKE_SOURCE_DIR}/docs/config WORKING_DIRECTORY ${CMAKE_SOURCE_DIR})
endif()

# Extract Strings
add_custom_target(extract-messages ${CMAKE_SOURCE_DIR}/scripts/extract-messages ${CMAKE_SOURCE_DIR})

# Build Translations
find_package(Gettext)

if(GETTEXT_FOUND)
    file(MAKE_DIRECTORY i18n)
    add_custom_target(translations)

    set(languages
        en
        x-test
    )
    foreach(lang ${languages})
        file(GLOB po_files resources/i18n/${lang}/*.po)
        foreach(file ${po_files})
            set(dir i18n/${lang})
            string(REGEX REPLACE ".*/(.*).po" "${dir}/\\1.mo" mofile ${file})
            add_custom_command(TARGET translations POST_BUILD COMMAND mkdir ARGS -p ${dir} COMMAND ${GETTEXT_MSGFMT_EXECUTABLE} ARGS ${file} -o ${mofile})
        endforeach()
    endforeach()
endif()
