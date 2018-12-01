import wx
import utils


class BooruInfoItem(wx.StaticText):
    def __init__(self, parent, label='', size=(300, 15), genre=None):
        self.size = wx.Size(size)
        self.genre = genre
        wx.StaticText.__init__(self, parent, label=label, size=size)
        self.SetFont(wx.Font(9, family=wx.FONTFAMILY_MODERN,
                             style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL))
        if not genre:
            self.SetForegroundColour(utils.FG_LIGHT)
        elif genre == 'general':
            self.SetForegroundColour(wx.Colour(239, 137, 129))  # pink
        elif genre == 'artist':
            self.SetForegroundColour(wx.Colour(211, 215, 15))  # yellow
        elif genre == 'copyright':
            self.SetForegroundColour(wx.Colour(204, 0, 162))  # purple
        elif genre == 'meta':
            self.SetForegroundColour(wx.Colour(230, 0, 0))  # red


class BooruInfoPanel(wx.Panel):
    def __init__(self, parent, label='<<Booru Info>>', size=(300, 400)):
        self.size = wx.Size(size)
        self.width, self.height = size
        wx.Panel.__init__(self, parent, size=size)

        self.title = wx.StaticText(self, size=(self.width, 24), label=label)
        self.title.SetFont(wx.Font(11, family=wx.FONTFAMILY_SCRIPT,
                                   style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_BOLD))
        self.title.SetForegroundColour(utils.FG_LIGHT)

        self.sizer = wx.GridBagSizer(0, 0)
        self.sizer.Add(self.title, pos=(0, 0), flag=wx.BOTTOM, border=0)
        self.SetSizerAndFit(self.sizer)

        self.info_items = {'artist': [], 'copyright': [], 'meta': [], 'general': []}
        self.num_items = 1

    def update(self, info):
        for i in reversed(range(1, self.num_items)):
            self.sizer.Remove(i)
        self.num_items = 1
        for genre in info:
            for data in info[genre]:
                item = BooruInfoItem(self, label=data, genre=genre)
                self.info_items[genre].append(item)
                self.num_items += 1
                self.sizer.Add(item, pos=(self.num_items-1, 0))
        self.sizer.Layout()
        self.Fit()

