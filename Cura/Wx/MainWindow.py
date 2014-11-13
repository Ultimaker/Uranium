import wx

from Cura.Wx.Canvas import Canvas
#from Cura.Wx.Panel import Panel

class MainWindow(wx.Frame):
    def __init__(self, title, app):
        super(MainWindow, self).__init__(None, wx.ID_ANY, title)
        
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_EXIT, "&Quit", "Close the application")
        
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        self.SetMenuBar(menuBar)
        
        canvas = Canvas(self, app)
