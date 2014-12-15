import wx

class Panel(wx.Frame):
    def __init__(self, parent):
        super(Panel, self).__init__(parent, style=wx.FRAME_FLOAT_ON_PARENT | wx.NO_BORDER | wx.FRAME_NO_TASKBAR | wx.FRAME_SHAPED)
        self.SetBackgroundColour(wx.SystemSettings.GetColour(wx.SYS_COLOUR_3DFACE))

        sizer = wx.BoxSizer(wx.VERTICAL)
        
        titleBar = wx.Panel(self)
        titleBar.SetBackgroundColour("black")
        
        contents = wx.Panel(self)
        #self._titleBar = InnerTitleBar(self, 'Profile')
        #self._titleBar.Bind(wx.EVT_LEFT_DOWN, self.onSmallToggle)
        #sizer.Add(self._titleBar, flag=wx.EXPAND)