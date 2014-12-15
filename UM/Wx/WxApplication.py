from UM.Application import Application

import wxversion
wxversion.select("2.8")
import wx

class WxApplication(Application, wx.App):
    def __init__(self):
        super(WxApplication, self).__init__()
        
    def run(self):
        self.MainLoop()