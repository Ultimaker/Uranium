# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

from typing import Dict
from PyQt5.QtGui import QOpenGLContext, QSurfaceFormat

from UM.Logger import Logger


class OpenGLContext(object):

    ##  Set OpenGL context, given major, minor version + core using QOpenGLContext
    #   Unfortunately, what you get back does not have to be the requested version.
    @classmethod
    def setContext(cls, major_version, minor_version, core = False, profile = None):
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

    ##  Check to see if the current OpenGL implementation has a certain OpenGL extension.
    #
    #   \param extension_name \type{string} The name of the extension to query for.
    #   \param ctx optionally provide context object to be used, or current context will be used.
    #
    #   \return True if the extension is available, False if not.
    @classmethod
    def hasExtension(cls, extension_name, ctx = None):
        if ctx is None:
            ctx = QOpenGLContext.currentContext()
        return ctx.hasExtension(bytearray(extension_name, "utf-8"))

    ##  Return if the current (or provided) context supports Vertex Array Objects
    #
    #   \param ctx (optional) context.
    @classmethod
    def supportsVertexArrayObjects(cls, ctx = None):
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

    ##  Set the default format for each new OpenGL context
    #   \param major_version
    #   \param minor_version
    #   \param core (optional) True for QSurfaceFormat.CoreProfile, False for CompatibilityProfile
    #   \param profile (optional) QSurfaceFormat.CoreProfile, CompatibilityProfile or NoProfile, overrules option core
    @classmethod
    def setDefaultFormat(cls, major_version, minor_version, core = False, profile = None):
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

    ##  Return if the OpenGL context version we ASKED for is legacy or not
    @classmethod
    def isLegacyOpenGL(cls):
        if cls.major_version < 4:
            return True
        if cls.major_version == 4 and cls.minor_version < 1:
            return True
        return False

    ##  Return "best" OpenGL to use, 4.1 core or 2.1.
    #   result is <major_version>, <minor_version>, <profile>
    #   The version depends on what versions are supported in Qt (4.1 and 2.0) and what
    #   the GPU supports. If creating a context fails at all, (None, None, None) is returned
    @classmethod
    def detectBestOpenGLVersion(cls):
        Logger.log("d", "Trying OpenGL context 4.1...")
        ctx = cls.setContext(4, 1, core = True)
        if ctx is not None:
            fmt = ctx.format()
            profile = fmt.profile()

            # First test: we hope for this
            if ((fmt.majorVersion() == 4 and fmt.minorVersion() >= 1) or (fmt.majorVersion() > 4)) and profile == QSurfaceFormat.CoreProfile:
                Logger.log("d",
                    "Yay, we got at least OpenGL 4.1 core: %s",
                    cls.versionAsText(fmt.majorVersion(), fmt.minorVersion(), profile))
                return 4, 1, QSurfaceFormat.CoreProfile
        else:
            Logger.log("d", "Failed to create OpenGL context 4.1.")

        # Fallback: check min spec
        Logger.log("d", "Trying OpenGL context 2.0...")
        ctx = cls.setContext(2, 0, profile = QSurfaceFormat.NoProfile)
        if ctx is not None:
            fmt = ctx.format()
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

    ##  Return OpenGL version number and profile as a nice formatted string
    @classmethod
    def versionAsText(cls, major_version, minor_version, profile):
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

    # to be filled by helper functions
    properties = {} # type: Dict[str, bool]
