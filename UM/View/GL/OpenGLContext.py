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
            self._supports_geometry_shader = True
        elif (ctx.hasExtension(bytearray("GL_EXT_geometry_shader4", "utf-8")) or ctx.hasExtension(bytearray("GL_ARB_geometry_shader4", "utf-8"))):
            self._supports_geometry_shader = True
            Logger.log("d", "Geometry shader is available on this machine, but don't know if it works.")
