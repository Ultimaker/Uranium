# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

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

    ##  Return whether the current context supports geometry shader
    @classmethod
    def supportsGeometryShader(cls, ctx=None):
        if ctx is None:
            ctx = QOpenGLContext.currentContext()
        format = ctx.format()
        major = format.majorVersion()
        minor = format.minorVersion()

        if major >= 4 or (major == 3 and minor >= 3):
            Logger.log("d", "OpenGL context version has geometry shader support.")
            return True
        elif (ctx.hasExtension(bytearray("GL_EXT_geometry_shader4", "utf-8")) or ctx.hasExtension(bytearray("GL_ARB_geometry_shader4", "utf-8"))):
            Logger.log("d", "Geometry shader is available on this machine, but don't know if it works.")
            return True
        else:
            Logger.log("d", "Not matching OpenGL version or extension for geometry shader.")
            return False

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

    @classmethod
    def isLegacyOpenGL(cls):
        if cls.major_version < 4:
            return True
        if cls.major_version == 4 and cls.minor_version < 1:
            return True
        return False

    ##  Return "best" OpenGL to use, 4.1 core or 2.1.
    #   result is <major_version>, <minor_version>, <profile>
    #   The version depends on what versions are supported in Qt (4.1 and 2.1) and what
    #   the GPU supports. If creating a context fails at all, (None, None, None) is returned
    @classmethod
    def detectBestOpenGLVersion(cls):
        ctx = cls.setContext(4, 1, core = True)

        if ctx is None:
            return None, None, None
        fmt = ctx.format()
        profile = fmt.profile()
        if fmt.majorVersion() >= 4 and fmt.minorVersion() >= 1 and profile == QSurfaceFormat.CoreProfile:
            return fmt.majorVersion(), fmt.minorVersion(), profile
        else:
            return 2, 1, QSurfaceFormat.NoProfile

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

    major_version = 0
    minor_version = 0
    profile = None

