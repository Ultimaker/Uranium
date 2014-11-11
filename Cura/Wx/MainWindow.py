import wx

class MainWindow(wx.Frame):
    def __init__(self, title):
        super(MainWindow, self).__init__(None, wx.ID_ANY, title)