set(CPACK_PACKAGE_VENDOR "Ultimaker")
set(CPACK_PACKAGE_CONTACT "Arjen Hiemstra <a.hiemstra@ultimaker.com>")
set(CPACK_PACKAGE_DESCRIPTION_SUMMARY "Uranium 3D Application Framework")
set(CPACK_PACKAGE_VERSION_MAJOR 15)
set(CPACK_PACKAGE_VERSION_MINOR 05)
set(CPACK_PACKAGE_VERSION_PATCH 90)

set(CPACK_RPM_PACKAGE_REQUIRES "python >= 3.3.0, python-arcus >= 15.05.90, python-qt5 >= 5.4.0")
set(CPACK_DEBIAN_PACKAGE_DEPENDS "python3 >= 3.3.0, python3-arcus >= 15.05.90, python-qt5 >= 5.4.0")

include(CPack)
