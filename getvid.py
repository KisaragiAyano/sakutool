import requests
import re
import os
import imageio
import wx
import numpy as np


class VidNotFoundError(IOError):
    def __init__(self, *args):
        self.args = args


class SakuVid:
    def __init__(self, booru_id, path='./asset/', maxsize=wx.Size(1024, 1024*9//16)):
        self.booru_id = booru_id
        self.path = path
        os.makedirs(path, exist_ok=True)
        self.vid_arr, self.booru_info = load_vid(booru_id, path)
        if not self.vid_arr:
            raise VidNotFoundError('')
            return

        self.vid_frames = len(self.vid_arr)
        self.height, self.width, self.nchannel = np.shape(self.vid_arr[0])
        self.size = wx.Size(self.width, self.height)
        vid = []
        for image_arr in self.vid_arr:
            image = wx.Bitmap.FromBuffer(self.width, self.height, image_arr)
            vid.append(image)
        self.vid = vid
        self.cur_frame_index = 0

        # scale
        maxw, maxh = maxsize
        w, h = self.width, self.height
        self.vid_scaled, self.w_scaled, self.h_scaled = None, None, None
        if w > maxw or h > maxh:
            ratio = w/maxw if w/maxw > h/maxh else h/maxh
            w_scaled, h_scaled = w/ratio, h/ratio
            vid = []
            for bitmap in self.vid:
                image = wx.ImageFromBitmap(bitmap)
                image.Scale(w_scaled, h_scaled)
                vid.append(image)
            self.vid_scaled, self.w_scaled, self.h_scaled = vid, w_scaled, h_scaled

    @property
    def w(self):
        return self.w_scaled if self.w_scaled else self.width

    @property
    def h(self):
        return self.h_scaled if self.h_scaled else self.height

    def cur_frame(self):
        vid = self.vid_scaled if self.vid_scaled else self.vid
        return vid[self.cur_frame_index]

    def next_frame(self):
        self.cur_frame_index += 1
        self.cur_frame_index %= self.vid_frames
        return self.cur_frame()

    def last_frame(self):
        self.cur_frame_index -= 1
        self.cur_frame_index %= self.vid_frames
        return self.cur_frame()


def load_vid(booru_id, path='./asset/'):
    booru_info, html = get_booru_info(booru_id)
    vid_path = get_vid(booru_id, path, html)
    if not vid_path:
        return None
    vid_reader = imageio.get_reader(vid_path, 'ffmpeg')

    # pylab.imshow(vid_reader.get_next_data())
    # pylab.show()
    vid = []
    try:
        for img in vid_reader:
            vid.append(img)
    except RuntimeError as e:
        pass
    # vid = [img for img in vid_reader]
    return vid, booru_info


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36\
            (KHTML, like Gecko) Chrome/34.0.1847.137 Safari/537.36 LBBROWSER'}


def get_vid(booru_id, path='./asset/', html=None):
    vid_path = path + '{}.{}'.format(booru_id, 'mp4')
    if os.path.exists(vid_path):
        return vid_path
    vid_path = path + '{}.{}'.format(booru_id, 'webm')
    if os.path.exists(vid_path):
        return vid_path
    return download_vid(booru_id, path, html)


def download_vid(booru_id, path='./asset/', html=None):
    if not html:
        booru_url = 'https://www.sakugabooru.com/post/show/{}'.format(booru_id)
        html = requests.get(booru_url, headers).text
    vid_url = re.findall('href=\"(http.*?\.mp4|http.*?\.webm)\"', html)
    if len(vid_url) == 0:
        return None
    vid_url = vid_url[0]
    vid_format = vid_url.split('.')[-1]

    path = path + '{}.{}'.format(booru_id, vid_format)
    with requests.get(vid_url, stream=True) as r:
        chunk_size = 1024
        # content_size = int(r.headers['content-length'])
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=chunk_size):
                f.write(chunk)
    return path


def get_booru_info(booru_id):
    booru_url = 'https://www.sakugabooru.com/post/show/{}'.format(booru_id)
    html = requests.get(booru_url, headers).text
    artist_data = re.findall('artist\" data-name=\"(.*?)\"', html)
    copyright_data = re.findall('copyright\" data-name=\"(.*?)\"', html)
    meta_data = re.findall('meta\" data-name=\"(.*?)\"', html)
    general_data = re.findall('general\" data-name=\"(.*?)\"', html)
    return {'artist': artist_data, 'copyright': copyright_data, 'meta': meta_data, 'general': general_data}, html
