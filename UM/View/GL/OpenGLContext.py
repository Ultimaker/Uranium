# Copyright (c) 2020 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Dict, Optional, Tuple, Any
from PyQt5.QtGui import QOpenGLVersionProfile, QOpenGLContext, QSurfaceFormat, QWindow

from UM.Logger import Logger
from UM.Platform import Platform


class OpenGLContext:
    class OpenGlVersionDetect:
        Autodetect = "autodetect"
        ForceLegacy = "force_legacy"
        ForceModern = "force_modern"

    @classmethod
    def setContext(cls, major_version: int, minor_version: int, core = False, profile = None):
        """Set OpenGL context, given major, minor version + core using QOpenGLContext
        Unfortunately, what you get back does not have to be the requested version.
        """
        new_format = QSurfaceFormat()
        new_format.setMajorVersion(major_version)
        new_format.setMinorVersion(minor_version)
        if core:
            profile_ = QSurfaceFormat.CoreProfile
        else:
            profile_ = QSurfaceFormat.CompatibilityProfile
        if profile is not None:
            profile_ = profile
        new_format.setProfile(profile_)

        new_context = QOpenGLContext()
        new_context.setFormat(new_format)
        success = new_context.create()
        if success:
            return new_context
        else:
            Logger.log("e", "Failed creating OpenGL context (%d, %d, core=%s)" % (major_version, minor_version, core))
            return None

    @classmethod
    def hasExtension(cls, extension_name: str, ctx = None) -> bool:
        """Check to see if the current OpenGL implementation has a certain OpenGL extension.

        :param extension_name: :type{string} The name of the extension to query for.
        :param ctx: optionally provide context object to be used, or current context will be used.

        :return: True if the extension is available, False if not.
        """
        if ctx is None:
            ctx = QOpenGLContext.currentContext()
        return ctx.hasExtension(bytearray(extension_name, "utf-8"))

    @classmethod
    def supportsVertexArrayObjects(cls, ctx = None) -> bool:
        """Return if the current (or provided) context supports Vertex Array Objects

        :param ctx: (optional) context.
        """
        if ctx is None:
            ctx = QOpenGLContext.currentContext()
        result = False
        if cls.major_version == 4 and cls.minor_version >= 1:
            result = True
        if not result and cls.major_version > 4:
            result = True
        if not result and cls.hasExtension("GL_ARB_vertex_array_object", ctx = ctx):
            result = True
        cls.properties["supportsVertexArrayObjects"] = result
        return result

    @classmethod
    def setDefaultFormat(cls, major_version: int, minor_version: int, core = False, profile = None) -> None:
        """Set the default format for each new OpenGL context
        :param major_version:
        :param minor_version:
        :param core: (optional) True for QSurfaceFormat.CoreProfile, False for CompatibilityProfile
        :param profile: (optional) QSurfaceFormat.CoreProfile, CompatibilityProfile or NoProfile, overrules option core
        """
        new_format = QSurfaceFormat()
        new_format.setMajorVersion(major_version)
        new_format.setMinorVersion(minor_version)
        if core:
            profile_ = QSurfaceFormat.CoreProfile
        else:
            profile_ = QSurfaceFormat.CompatibilityProfile
        if profile is not None:
            profile_ = profile
        new_format.setProfile(profile_)

        QSurfaceFormat.setDefaultFormat(new_format)
        cls.major_version = major_version
        cls.minor_version = minor_version
        cls.profile = profile_

    @classmethod
    def isLegacyOpenGL(cls) -> bool:
        """Return if the OpenGL context version we ASKED for is legacy or not"""
        if cls.major_version < 4:
            return True
        if cls.major_version == 4 and cls.minor_version < 1:
            return True
        return False

    @classmethod
    def detectBestOpenGLVersion(cls, force_compatability: bool) -> Tuple[Optional[int], Optional[int], Optional[int]]:
        """Return "best" OpenGL to use, 4.1 core or 2.0.

        result is <major_version>, <minor_version>, <profile>
        The version depends on what versions are supported in Qt (4.1 and 2.0) and what
        the GPU supports. If creating a context fails at all, (None, None, None) is returned
        Note that PyQt only supports 4.1, 2.1 and 2.0. Cura omits support for 2.1, so the
        only returned options are 4.1 and 2.0.
        """
        cls.detect_ogl_context = None
        if not force_compatability:
            Logger.log("d", "Trying OpenGL context 4.1...")
            cls.detect_ogl_context = cls.setContext(4, 1, core = True)
        if cls.detect_ogl_context is not None:
            fmt = cls.detect_ogl_context.format()
            profile = fmt.profile()

            # First test: we hope for this
            if ((fmt.majorVersion() == 4 and fmt.minorVersion() >= 1) or (fmt.majorVersion() > 4)) and profile == QSurfaceFormat.CoreProfile:
                Logger.log("d",
                    "Yay, we got at least OpenGL 4.1 core: %s",
                    cls.versionAsText(fmt.majorVersion(), fmt.minorVersion(), profile))

                # https://riverbankcomputing.com/pipermail/pyqt/2017-January/038640.html
                # PyQt currently only implements 2.0, 2.1 and 4.1Core
                # If eg 4.5Core would be detected and used here, PyQt would not be able to handle it.
                major_version = 4
                minor_version = 1

                # CURA-6092: Check if we're not using software backed 4.1 context; A software 4.1 context
                # is much slower than a hardware backed 2.0 context
                # Check for OS, Since this only seems to happen on specific versions of Mac OSX and
                # the workaround (which involves the deletion of an OpenGL context) is a problem for some Intel drivers.
                if not Platform.isOSX():
                    return major_version, minor_version, QSurfaceFormat.CoreProfile

                gl_window = QWindow()
                gl_window.setSurfaceType(QWindow.OpenGLSurface)
                gl_window.showMinimized()

                cls.detect_ogl_context.makeCurrent(gl_window)

                gl_profile = QOpenGLVersionProfile()
                gl_profile.setVersion(major_version, minor_version)
                gl_profile.setProfile(profile)

                gl = cls.detect_ogl_context.versionFunctions(gl_profile) # type: Any #It's actually a protected class in PyQt that depends on the requested profile and the implementation of your graphics card.

                gpu_type = "Unknown"  # type: str

                result = None
                if gl:
                    result = gl.initializeOpenGLFunctions()

                if not result:
                    Logger.log("e", "Could not initialize OpenGL to get gpu type")
                else:
                    # WORKAROUND: Cura/#1117 Cura-packaging/12
                    # Some Intel GPU chipsets return a string, which is not undecodable via PyQt5.
                    # This workaround makes the code fall back to a "Unknown" renderer in these cases.
                    try:
                        gpu_type = gl.glGetString(gl.GL_RENDERER)
                    except UnicodeDecodeError:
                        Logger.log("e", "DecodeError while getting GL_RENDERER via glGetString!")

                Logger.log("d", "OpenGL renderer type for this OpenGL version: %s", gpu_type)
                if "software" in gpu_type.lower():
                    Logger.log("w", "Unfortunately OpenGL 4.1 uses software rendering")
                else:
                    return major_version, minor_version, QSurfaceFormat.CoreProfile
        else:
            Logger.log("d", "Failed to create OpenGL context 4.1.")

        # Fallback: check min spec
        Logger.log("d", "Trying OpenGL context 2.0...")
        cls.detect_ogl_context = cls.setContext(2, 0, profile = QSurfaceFormat.NoProfile)
        if cls.detect_ogl_context is not None:
            fmt = cls.detect_ogl_context.format()
            profile = fmt.profile()

            if fmt.majorVersion() >= 2 and fmt.minorVersion() >= 0:
                Logger.log("d",
                    "We got at least OpenGL context 2.0: %s",
                    cls.versionAsText(fmt.majorVersion(), fmt.minorVersion(), profile))
                return 2, 0, QSurfaceFormat.NoProfile
            else:
                Logger.log("d",
                    "Current OpenGL context is too low: %s" % cls.versionAsText(fmt.majorVersion(), fmt.minorVersion(),
                        profile))
                return None, None, None
        else:
            Logger.log("d", "Failed to create OpenGL context 2.0.")
            return None, None, None

    @classmethod
    def versionAsText(cls, major_version: int, minor_version: int, profile) -> str:
        """Return OpenGL version number and profile as a nice formatted string"""
        if profile == QSurfaceFormat.CompatibilityProfile:
            xtra = "Compatibility profile"
        elif profile == QSurfaceFormat.CoreProfile:
            xtra = "Core profile"
        elif profile == QSurfaceFormat.NoProfile:
            xtra = "No profile"
        else:
            xtra = "Unknown profile"
        return "%s.%s %s" % (major_version, minor_version, xtra)

    # Global values, OpenGL context versions we ASKED for (not per se what we got)
    major_version = 0
    minor_version = 0
    profile = None  # type: QSurfaceFormat

    # Keep already created context in memory, as some drivers (Intel) have trouble deleting OpenGL-contexts:
    detect_ogl_context = None  #type: Optional[QOpenGLContext]

    # To be filled by helper functions
    properties = {}  # type: Dict[str, bool]
