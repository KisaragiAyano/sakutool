import wx
import utils


class TimelinePanel(wx.Panel):
    def __init__(self, parent, size=(1024, 80)):
        self.size = size
        self.width, self.height = size
        wx.Panel.__init__(self, parent, size=size)
        self.SetBackgroundColour(utils.BG_LIGHT)
        # timeline_title = wx.StaticText(self, label='Timeline Panel: to be continued...')

        sizer = wx.GridBagSizer(0, 0)

        self.__build_progress_panel()

        sizer.Add(self.progress_panel, pos=(0, 0), span=(1, 1), flag=wx.ALL, border=0)

        self.set_progress(0.)

    def __build_progress_panel(self):
        self.progress_panel = wx.Panel(self, size=(self.width, 20))
        self.progress_panel.SetBackgroundColour(utils.BLACK)
        self.progress_bar = wx.Panel(self.progress_panel, size=(self.width, 12), pos=(0, 4))
        self.progress_bar.SetBackgroundColour(utils.GRAY)

        self.progress_bar.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.progress_bar.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        # self.progress_panel.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        self.progress_panel.Bind(wx.EVT_KEY_DOWN, utils.event_skip)

    def set_progress(self, p):
        p = 0. if p < 0. else p
        p = 1. if p > 1. else p
        w = self.size[0]
        x = (p - 1)*w
        self.progress_bar.SetPosition((x, 4))
