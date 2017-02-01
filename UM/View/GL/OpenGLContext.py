# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtGui import QOpenGLContext, QSurfaceFormat

from UM.Logger import Logger


class OpenGLContext(object):

    ##  Set OpenGL context, given major, minor version + core using QOpenGLContext
    #   Unfortunately, what you get back does not have to be the requested version.
    @classmethod
    def setContext(self, major_version, minor_version, core = False):
        new_format = QSurfaceFormat()
        new_format.setMajorVersion(major_version)
        new_format.setMinorVersion(minor_version)
        if core:
            new_format.setProfile(QSurfaceFormat.CoreProfile)
        else:
            new_format.setProfile(QSurfaceFormat.CompatibilityProfile)
        new_context = QOpenGLContext()
        new_context.setFormat(new_format)
        success = new_context.create()
        if success:
            ctx = QOpenGLContext.currentContext()
            Logger.log("d", "Context: %s" % ctx)
            fmt = ctx.format()
            profile = fmt.profile()
            if profile == QSurfaceFormat.CompatibilityProfile:
                xtra = "Compatibility profile"
            elif profile == QSurfaceFormat.CoreProfile:
                xtra = "Core profile"
            elif profile == QSurfaceFormat.NoProfile:
                xtra = "No profile"
            else:
                xtra = "Unknown profile"
            Logger.log(
                "d", "Successfully created OpenGL context, requested (%d, %d, core=%s), actual is (%d, %d, %s)" % (
                    major_version, minor_version, core, fmt.majorVersion(), fmt.minorVersion(), xtra))
            return ctx
        else:
            Logger.log("e", "Failed creating OpenGL context (%d, %d, core=%s)" % (major_version, minor_version, core))

    @classmethod
    def supportsGeometryShader(self, ctx=None):
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
    @classmethod
    def setDefaultFormat(cls, major_version, minor_version, core = False):
        new_format = QSurfaceFormat()
        new_format.setMajorVersion(major_version)
        new_format.setMinorVersion(minor_version)
        if core:
            profile = QSurfaceFormat.CoreProfile
        else:
            profile = QSurfaceFormat.CompatibilityProfile
        new_format.setProfile(profile)

        QSurfaceFormat.setDefaultFormat(new_format)
        cls.major_version = major_version
        cls.minor_version = minor_version
        cls.profile = profile

    @classmethod
    def isLegacyOpenGL(cls):
        if cls.major_version < 4:
            return True
        if cls.major_version == 4 and cls.minor_version < 1:
            return True
        return False

    major_version = 0
    minor_version = 0
    profile = None

