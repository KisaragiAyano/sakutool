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

        self.set_start_progress(self._start_progress)

        self.set_progress(0.)

    def __build_progress_panel(self):
        self.progress_panel = wx.Panel(self, size=(self.width, 20))
        self.progress_panel.SetBackgroundColour(utils.BLACK)
        self.progress_bar = wx.Panel(self.progress_panel, size=(self.width, 12), pos=(0, 4))
        self.progress_bar.SetBackgroundColour(utils.GRAY)
        self.progress_cursor = wx.Panel(self.progress_bar, size=(1, 12), pos=(0, 0))
        self.progress_cursor.SetBackgroundColour(utils.WHITE)
        self.progress_cursor_out = wx.Panel(self.progress_panel, size=(1, 12), pos=(0, 4))
        self.progress_cursor_out.SetBackgroundColour(utils.GRAY)
        self.progress_cursor_out.Show(False)

        self.progress_bar.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.progress_bar.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        self.progress_cursor.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.progress_cursor.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        # self.progress_panel.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        self.progress_panel.Bind(wx.EVT_KEY_DOWN, utils.event_skip)

        self._start_progress = 0.
        self._end_progress = 1.

    def reset(self):
        self._start_progress = 0.
        self._end_progress = 1.
        self.set_start_progress(0.)

    def set_progress(self, p):
        p = 0. if p < 0. else p
        p = 1. if p > 1. else p
        # x = (p - 1)*self.width
        # self.progress_bar.SetPosition((x, 4))
        if self._start_progress <= p <= self._end_progress:
            x = int((p - self._start_progress)*(self.width-1))
            self.progress_cursor_out.Show(False)
            self.progress_cursor.SetPosition((x, 0))
            self.progress_cursor.Show(True)
        else:
            x = p*(self.width-1)
            self.progress_cursor.Show(False)
            self.progress_cursor_out.SetPosition((x, 4))
            self.progress_cursor_out.Show(True)

    def set_start_progress(self, p):
        p = 0. if p < 0. else p
        p = 1. if p > 1. else p
        if p >= self._end_progress:
            return False
        self._start_progress = p
        x = p*(self.width-1)
        w = (self._end_progress - self._start_progress)*(self.width-1)+1
        self.progress_bar.SetSize((w, 12))
        self.progress_bar.SetPosition((x, 4))
        self.set_progress(p)
        return True

    def set_end_progress(self, p):
        p = 0. if p < 0. else p
        p = 1. if p > 1. else p
        if p <= self._start_progress:
            return False
        self._end_progress = p
        # x = p*(self.width-1)
        w = (self._end_progress - self._start_progress)*(self.width-1)+1
        self.progress_bar.SetSize((w, 12))
        self.set_progress(p)
        return True


