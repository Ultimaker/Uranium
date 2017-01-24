# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the AGPLv3 or higher.

from PyQt5.QtGui import QOpenGLVersionProfile, QOpenGLContext, QSurfaceFormat

from UM.Logger import Logger


class Context(object):

    ##  Set OpenGL context, given major, minor version + core using QOpenGLContext
    #   Unfortunately, what you get back does not have to be the requested version.
    @classmethod
    def setContext(self, major_version, minor_version, core = False):
        profile = QOpenGLVersionProfile()
        profile.setVersion(major_version, minor_version)
        if core:
            profile.setProfile(QSurfaceFormat.CoreProfile)
        success = QOpenGLContext().create()
        if success:
            ctx = QOpenGLContext.currentContext()
            fmt = ctx.format()
            Logger.log(
                "d", "Successfully created OpenGL context, requested (%d, %d, core=%s), actual is (%d, %d)" % (
                    major_version, minor_version, core, fmt.majorVersion(), fmt.minorVersion()))
            return ctx
        else:
            Logger.log("e", "Failed creating OpenGL context (%d, %d, core=%s)" % (major_version, minor_version, core))
