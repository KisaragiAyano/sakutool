import wx
import configparser
import os
import time


WHITE = wx.Colour(255, 255, 255)
LIGHT_GRAY = wx.Colour(222, 222, 222)
MID_GRAY = GRAY = wx.Colour(128, 128, 128)
DARK_GRAY = wx.Colour(33, 33, 33)
BLACK = wx.Colour(0, 0, 0)

TRANSPARENT = wx.Colour(0, 0, 0, 0)

FG_DARK = wx.Colour(33, 33, 33)
FG_LIGHT = wx.Colour(222, 222, 222)
BG_DARK = wx.Colour(33, 33, 33)
BG_LIGHT = wx.Colour(177, 177, 177)


class Configer:
    def __init__(self, path='./config.ini'):
        self.path = path
        self.config = configparser.ConfigParser()
        init_flag = False
        if not os.path.exists(path):
            init_flag = True
        else:
            try:
                self.config.read('./config.ini')
                self.asset_path = self.config['DEFAULT']['PATH']
            except:
                init_flag = True

        if init_flag:
            with open('./config.ini', 'w') as configfile:
                self.config['DEFAULT'] = {'PATH': './asset/'}
                self.asset_path = './asset/'
                self.config.write(configfile)

        # user_path = os.path.expanduser('~/')
    def __call__(self, *args, **kwargs):
        return self.config

    def get_asset_path(self):
        return self.asset_path


def search(path, name):
    import re
    vids = []
    if not name:
        name = '[0-9]'
    for parent, dirNames, fileNames in os.walk(path):
        for fileName in fileNames:
            r = '^{}.*?\.webm'.format(name)
            res = re.search(r, fileName)
            r = '^{}.*?\.mp4'.format(name)
            res = res or re.search(r, fileName)
            if res:
                vids.append(fileName.split('.')[0])
    return vids


def event_skip(event):
    event.ResumePropagation(9)
    event.Skip()


def sec2time(s):
    m, s = divmod(s, 60)
    h, m = divmod(m, 60)
    return "%02d:%02d:%05.2f" % (h, m, s)

