import wx
from wx import glcanvas

from OpenGL import GL

class Canvas(glcanvas.GLCanvas):
    def __init__(self, parent, app):
        attribList = [
            glcanvas.WX_GL_RGBA,
            glcanvas.WX_GL_DOUBLEBUFFER,
            glcanvas.WX_GL_DEPTH_SIZE, 24,
            glcanvas.WX_GL_STENCIL_SIZE, 8,
            0
        ]
        super(Canvas, self).__init__(parent, style=wx.WANTS_CHARS|wx.CLIP_CHILDREN, attribList = attribList)

        self._app = app
        self._context = glcanvas.GLContext(self)

        wx.EVT_PAINT(self, self._onPaint)

    def _onPaint(self, event):
        wx.PaintDC(self) # Make a PaintDC, else the paint event will be called again.
        self.SetCurrent(self._context)
        self._app.getController().getActiveView().render(self._context)
        GL.glFlush()
        self.SwapBuffers()
