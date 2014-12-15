import wx
from wx import glcanvas

from OpenGL import GL
from OpenGL import GLU

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
        self._backgroundColor = wx.Colour(204, 204, 204, 255)
        self._context = glcanvas.GLContext(self)
        self._updateTriggered = False

        wx.EVT_PAINT(self, self._onPaint)

        # Set up relevant context-related properties after the first time the event loop has run.
        # This is because the context needs the event loop to run to be properly initialized.
        wx.CallAfter(self._initializeContext)

    ## Trigger an update of the canvas.
    def update(self):
        if not self._updateTriggered:
            self._updateTriggered = True
            wx.CallAfter(self.Refresh)

    def setBackgroundColor(self, color):
        self._backgroundColor = color
        GL.glClearColor(
            self._backgroundColor.Red() /255.0,
            self._backgroundColor.Green() / 255.0,
            self._backgroundColor.Blue() / 255.0,
            self._backgroundColor.Alpha() / 255.0
        )

    # Private
    # WxWidgets paint event
    def _onPaint(self, event):
        wx.PaintDC(self) # Make a PaintDC, else the paint event will be called again.

        self.SetCurrent(self._context)
        size = self.GetSize()
        GL.glViewport(0, 0, size.GetWidth(), size.GetHeight())

        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        GL.glOrtho(-5, 5, -5, 5, -5, 5)
        #GLU.gluPerspective(45.0, size.GetWidth() / size.GetHeight(), 0, 100)

        GL.glMatrixMode(GL.GL_MODELVIEW)
        GL.glLoadIdentity()

        # Render the view. The view is responsible for rendering everything relating to the scene.
        self._app.getController().getActiveView().render()

        GL.glFlush()
        self.SwapBuffers()

    # Private
    # Set up context related properties
    def _initializeContext(self):
        self.SetCurrent(self._context)
        GL.glClearColor( #WTF Wx, y u no have float getter?
            self._backgroundColor.Red() /255.0,
            self._backgroundColor.Green() / 255.0,
            self._backgroundColor.Blue() / 255.0,
            self._backgroundColor.Alpha() / 255.0
        )
