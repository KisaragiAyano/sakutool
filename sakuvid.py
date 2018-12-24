import requests
import re
import os
import wx
import numpy as np

import cv2
from ffpyplayer.player import MediaPlayer


def save_image(uri, im):
    im = cv2.cvtColor(im, cv2.COLOR_RGB2BGR)
    cv2.imwrite(uri, im)


class VidNotFoundError(IOError):
    def __init__(self, *args):
        self.args = args


class VidFile:
    def __init__(self, path, maxsize=wx.Size(1024, 1024*9//16)):
        self.vid = vid = cv2.VideoCapture(path)
        # self.audio = MediaPlayer(path)
        self.vid_frames = vid.get(cv2.CAP_PROP_FRAME_COUNT)
        self.height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.fps = vid.get(cv2.CAP_PROP_FPS)

        self.cur_frame_index = 0

        # scale
        maxw, maxh = maxsize
        w, h = self.width, self.height
        self.w_scaled, self.h_scaled = None, None
        if w > maxw or h > maxh:
            ratio = w / maxw if w / maxw > h / maxh else h / maxh
            self.w_scaled, self.h_scaled = int(w / ratio), int(h / ratio)

    @property
    def w(self):
        return self.w_scaled if self.w_scaled else self.width

    @property
    def h(self):
        return self.h_scaled if self.h_scaled else self.height

    def get_current_frame(self):
        img = self._read()
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, self.cur_frame_index)
        return img

    def get_relative_frame(self, n):
        index = (self.cur_frame_index + n) % self.vid_frames
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, index)
        img = self._read()
        self.vid.set(cv2.CAP_PROP_POS_FRAMES, self.cur_frame_index)
        return img

    def shift_index(self, k=1):
        self.cur_frame_index += k
        self.cur_frame_index %= self.vid_frames

    def seek(self, n):
        self.cur_frame_index = n
        self.cur_frame_index %= self.vid_frames

    def frame_next(self, k=1):
        img = self._read()
        self.cur_frame_index = self.vid.get(cv2.CAP_PROP_POS_FRAMES)
        if self.cur_frame_index >= self.vid_frames:
            self.cur_frame_index = 0
            self.vid.set(cv2.CAP_PROP_POS_FRAMES, self.cur_frame_index)
        return img

    def save_frame(self):
        pass

    def _read(self):
        ret, img = self.vid.read()
        if self.w_scaled:
            img = cv2.resize(img, (self.w_scaled, self.h_scaled))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        return img

    def release(self):
        self.vid.release()


class SakuVid:
    def __init__(self, booru_id, path='./asset/', maxsize=wx.Size(1024, 1024*9//16)):
        self.booru_id = booru_id
        self.path = path
        os.makedirs(path, exist_ok=True)

        self.booru_info, html = get_booru_info(booru_id)
        vid_path = get_vid(booru_id, path, html)
        if not vid_path:
            raise VidNotFoundError('')
            return
        cap = cv2.VideoCapture(vid_path)
        self.fps = cap.get(cv2.CAP_PROP_FPS)
        self.height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)

        vid = []
        while cap.isOpened():
            ret, img = cap.read()
            if not ret:
                break
            vid.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        cap.release()
        # self.vid_arr, self.booru_info = load_vid(booru_id, path)
        # if not self.vid_arr:
        #     raise VidNotFoundError('')
        #     return

        self.vid_frames = len(vid)
        self.size = wx.Size(self.width, self.height)

        self.vid = vid
        self.cur_frame_index = 0

        # scale
        maxw, maxh = maxsize
        w, h = self.width, self.height
        self.vid_scaled, self.w_scaled, self.h_scaled = None, None, None
        if w > maxw or h > maxh:
            ratio = w/maxw if w/maxw > h/maxh else h/maxh
            w_scaled, h_scaled = int(w/ratio), int(h/ratio)
            vid = []
            for img in self.vid:
                # image = wx.ImageFromBitmap(bitmap)
                # image.Scale(w_scaled, h_scaled)
                image = cv2.resize(img, (w_scaled, h_scaled))
                vid.append(image)
            self.vid_scaled, self.w_scaled, self.h_scaled = vid, w_scaled, h_scaled

    @property
    def w(self):
        return self.w_scaled if self.w_scaled else self.width

    @property
    def h(self):
        return self.h_scaled if self.h_scaled else self.height

    def get_current_frame(self):
        vid = self.vid_scaled if self.vid_scaled else self.vid
        return vid[self.cur_frame_index]

    def get_relative_frame(self, n):
        n = self.cur_frame_index + n
        n %= self.vid_frames
        vid = self.vid_scaled if self.vid_scaled else self.vid
        return vid[n]

    def shift_index(self, k=1):
        self.cur_frame_index += k
        self.cur_frame_index %= self.vid_frames

    def seek(self, n):
        self.cur_frame_index = n
        self.cur_frame_index %= self.vid_frames

    def frame_next(self, k=1):
        img = self.get_current_frame()
        self.shift_index(k)
        return img

    def save_frame(self):
        uri = self.path + '{}/'.format(self.booru_id)
        os.makedirs(uri, exist_ok=True)
        index = self.cur_frame_index
        uri += '{}.jpg'.format(index)
        if not os.path.exists(uri):
            im = self.vid[index]
            save_image(uri=uri, im=im)


# def load_vid(booru_id, path='./asset/'):
#     booru_info, html = get_booru_info(booru_id)
#     vid_path = get_vid(booru_id, path, html)
#     if not vid_path:
#         return None, None
#
#     vid = []
#     vid_reader = cv2.VideoCapture(vid_path)
#     while(vid_reader.isOpened()):
#         ret, img = vid_reader.read()
#         if not ret:
#             break
#         vid.append(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
#     vid_reader.release()
#
#     return vid, booru_info


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
