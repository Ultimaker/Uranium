# Ultimaker uniform Python linking method
function(use_python project_name)
    set(COMPONENTS ${ARGN})
    if(NOT DEFINED Python_VERSION)
        set(Python_VERSION
                3.8
                CACHE STRING "Python Version" FORCE)
        message(STATUS "Setting Python version to ${Python_VERSION}. Set Python_VERSION if you want to compile against an other version.")
    endif()
    if(APPLE)
        set(Python_FIND_FRAMEWORK NEVER)
    endif()
    find_package(Python ${Python_VERSION} EXACT REQUIRED COMPONENTS ${COMPONENTS})
    target_link_libraries(${project_name} PRIVATE Python::Python)
    target_include_directories(${project_name} PUBLIC ${Python_INCLUDE_DIRS})
    message(STATUS "Linking and building ${project_name} against Python ${Python_VERSION}")
endfunction()
