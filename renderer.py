import wx
import time
import threading
import cv2
import numpy as np
import time


class RenderThread(threading.Thread):
    def __init__(self, func, fps=24.):
        threading.Thread.__init__(self)
        self.func = func
        self._fps = fps
        self._flag_stop = threading.Event()
        self._flag_stop.set()
        self._flag_pause = threading.Event()
        self._flag_pause.set()

    def stop(self):
        self._flag_stop.clear()
        self._flag_pause.set()

    def play_pause(self):
        if self._flag_pause.isSet():
            self._flag_pause.clear()
        else:
            self._flag_pause.set()

    def pause(self):
        if self._flag_stop.isSet():
            self._flag_pause.clear()

    def resume(self):
        self._flag_pause.set()

    def run(self):
        t = time.time()
        while self._flag_stop.isSet():
            self._flag_pause.wait()
            self.func()

            t = time.time() - t
            sleep_t = max(0., 1./self._fps - t - 0.001)
            time.sleep(sleep_t)
            t = time.time()

    def set_fps(self, fps):
        fps = max(1., fps)
        fps = min(24., fps)
        self._fps = fps


class Renderer(wx.Panel):
    def __init__(self, parent, ext_print, size=(1024, 576)):
        self.size = size
        self.width, self.height = size
        wx.Panel.__init__(self, parent, size=size)
        self.SetBackgroundColour('black')
        self.ext_print = ext_print

        grid_img = np.array(
            [[[0, 0, 0, 128] if (w % 80 == 0 or h % 80 == 0) else [0, 0, 0, 0] for w in range(self.width)] for h in
             range(self.height)],
            dtype=np.uint8)
        self._grid_img_black = wx.Bitmap.FromBufferRGBA(self.width, self.height, grid_img)
        # grid_img = np.array(
        #     [[[255, 255, 255, 100] if (w % 80 == 0 or h % 80 == 0) else [0, 0, 0, 0] for w in range(self.width)] for h in
        #      range(self.height)],
        #     dtype=np.uint8)
        # self._grid_img_white = wx.Bitmap.FromBufferRGBA(self.width, self.height, grid_img)

        self._render_thread = None
        self.vid = None
        self._is_playing = False
        self._buffer = wx.NullBitmap
        self._fps = 24.
        self._canny_on = 0
        self._grid_on = 0
        self._k = 2
        self._onion_num = 0
        self._onion_buffer = {}

        self._img_woff = None
        self._img_hoff = None

    def load_vid(self, vid):
        self.stop()
        self.vid = vid
        self._img_woff = (self.width - self.vid.w)/2
        self._img_hoff = (self.height - self.vid.h)/2

        self._onion_buffer = {}
        self._fps = 24.

        # self.cur_frame()
        self._build_render_thread()


    def _build_render_thread(self):
        self._render_thread = RenderThread(self._next_frame_render, fps=self._fps/self._k)
        self._render_thread.start()
        self._is_playing = True

    # auto play control
    def play_pause(self):
        if self._render_thread:
            self._is_playing = not self._is_playing
            self._render_thread.play_pause()

    def pause(self):
        if self._render_thread and self._is_playing:
            self._is_playing = False
            self._render_thread.pause()

    def stop(self):
        if self._render_thread:
            self._is_playing = False
            self._render_thread.stop()
            self._render_thread.join(2.)
            self._render_thread.stop()
            self._render_thread = None

    def _next_frame_render(self):
        if self.vid and self._is_playing:
            img = self.vid.next_frame(self._k)
            self._render_frame()

    def switch_fps(self):
        if self.vid and self._render_thread:
            if self._fps == 24.:
                self._fps = 12.
            elif self._fps == 12.:
                self._fps = 6.
            else:
                self._fps = 24.
            self._render_thread.set_fps(self._fps / self._k)
        self.refresh_info()

    # manual play
    def last_frame(self):
        if self.vid:
            self.pause()
            img = self.vid.last_frame(self._k)
            self._render_frame()

    def next_frame(self):
        if self.vid:
            self.pause()
            img = self.vid.next_frame(self._k)
            self._render_frame()

    def cur_frame(self):
        if self.vid:
            self.pause()
            # img = self.vid.cur_frame()
            self._render_frame()

    # operation handler
    def switch_canny(self):
        self._canny_on = (self._canny_on + 1) % 3
        if not self._is_playing:
            self.cur_frame()

    def switch_k(self):
        self._k = self._k % 3 + 1
        self._render_thread.set_fps(self._fps / self._k)
        if not self._is_playing:
            self.cur_frame()

    def switch_onion(self):
        self._onion_num = (self._onion_num + 1) % 4
        if not self._is_playing:
            self.cur_frame()

    def switch_grid(self):
        self._grid_on = (self._grid_on + 1) % 2
        if not self._is_playing:
            self.cur_frame()

    # info
    def refresh_info(self):
        info_str = ' Playing Info \n\n'
        info_str += 'FPS of playing: {}\n'.format(self._fps)
        if self.vid:
            info_str += 'No. of frames: {}/{}\n'.format(self.vid.cur_frame_index, self.vid.vid_frames)
        else:
            pass
        info_str += 'Canny Mode: {}\n'.format('On' if self._canny_on else 'Off')
        info_str += 'Komas with \'j\'/\'k\': {}\n'.format(self._k)
        info_str += 'Onion num: {}\n'.format(self._onion_num)
        self.ext_print(info_str)

    def _render_frame(self):
        if not self._canny_on:
            img = self._render_onion()
        elif self._canny_on == 1:
            img = self._render_onion_canny()
            img_color = (img/255. * self.vid.cur_frame()).astype(np.uint8)
            img = cv2.addWeighted(img, 0.5, img_color, 0.5, 0)
        else:
            canny = self._render_onion_canny()/255.
            img = self._render_onion()
            img_canny = (img * canny).astype(np.uint8)
            img = cv2.addWeighted(img, 0.5, img_canny, 0.8, 0)

        dc = wx.BufferedDC(wx.ClientDC(self), self._buffer)
        # dc.Clear()
        bitmap = wx.Bitmap.FromBuffer(self.vid.w, self.vid.h, img)
        dc.DrawBitmap(bitmap, self._img_woff, self._img_hoff)
        if self._grid_on:
            dc.DrawBitmap(self._grid_img_black, 0, 0)
        self.refresh_info()

    def render_clear(self):
        dc = wx.BufferedDC(wx.ClientDC(self), self._buffer)
        dc.Clear()

    def _render_onion(self):
        onion_num = self._onion_num
        imgs = []
        for n in np.arange(-onion_num * self._k, 1, self._k):
            im = self.vid.get_relative_frame(n)
            imgs.append(im)
        maximgs = np.max(imgs, axis=0)
        minimgs = np.min(imgs, axis=0)
        meanimgs = np.mean([maximgs, minimgs], axis=0)
        meanimgs = meanimgs.astype(np.uint8)
        for i, im in enumerate(imgs):
            if not i:
                img = im
            else:
                img = cv2.addWeighted(img, 1. - 1. / (i + 2 - 0.3), im, 1. / (i + 2 - 0.3), 0)
        img = cv2.addWeighted(meanimgs, 0.5, img, 0.5, 0)
        return img

    def _render_onion_canny(self):
        onion_num = self._onion_num
        ns = np.arange(-onion_num * self._k, 1, self._k)
        indexes = [(self.vid.cur_frame_index + n) % self.vid.vid_frames for n in ns]
        for i, n in enumerate(ns):
            index = indexes[i]
            if index not in self._onion_buffer:
                im = self.vid.get_relative_frame(n)
                self._onion_buffer[index] = self._canny(im)

        masks = []
        for i, n in enumerate(ns):
            index = indexes[i]
            if i:
                im = self._onion_buffer[index]
                im_ = self._onion_buffer[indexes[i - 1]]
                if not masks:
                    _, mask = cv2.threshold(cv2.absdiff(im, im_), thresh=25, maxval=255, type=cv2.THRESH_BINARY)
                    masks.append(mask)
                    masks.append(mask)
                else:
                    _, mask = cv2.threshold(cv2.absdiff(im, im_), thresh=25, maxval=255, type=cv2.THRESH_BINARY)
                    masks.append(mask)

        # t = time.time()
        for i, n in enumerate(ns):
            index = indexes[i]
            if not i:
                if not onion_num:
                    img = cv2.cvtColor(self._onion_buffer[index], cv2.COLOR_GRAY2RGB)
                else:
                    img = cv2.bitwise_and(self._onion_buffer[index], self._onion_buffer[index], mask=masks[i])
                    img = self._monocolor(img, onion_num - i)
                    # img = self._denoise(img)
            elif n < 0:
                im = cv2.bitwise_and(self._onion_buffer[index], self._onion_buffer[index], mask=masks[i])
                im = cv2.bitwise_and(im, im, mask=masks[i+1])
                im = self._monocolor(im, onion_num - i)
                # im = self._denoise(im)
                img = cv2.addWeighted(img, 0.75, im, 1., 0)
            else:
                im = cv2.bitwise_and(self._onion_buffer[index], self._onion_buffer[index], mask=masks[i])
                im = self._monocolor(im, onion_num - i)
                # im = self._denoise(im)
                img = cv2.addWeighted(img, 0.75, im, 1., 0)
            img = self._denoise(img)
        # print(t-time.time())
        return img

    # image process
    def _canny(self, img):
        img = res = cv2.medianBlur(img, 3)
        edge = res = cv2.Canny(img, 60, 110)
        # edge_rgb = res = cv2.cvtColor(edge, cv2.COLOR_GRAY2RGB)
        # edge_color = res = np.array(edge_rgb/255. * img, dtype=np.uint8)
        # if self._canny_on == 2:     # colored
            # fil = np.array([[-1, 0, 0, 0, 0], [0, 1, 0, 0, 0], [0, 0, 1, 0, 0],
            #                 [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]])
            # mask = cv2.filter2D(edge_color, -1, fil)
            # _, mask = cv2.threshold(mask, thresh=10, maxval=255, type=cv2.THRESH_BINARY)
            # res = np.array(mask / 255. * edge_color, dtype=np.uint8)

        return res

    def _monocolor(self, im, n):
        color = np.array([[[1, 0.3, 0.3], [0.65, 0.55, 0.2], [0.2, 0.6, 0.2], [0.2, 0.5, 0.5], [0.2, 0.2, 1]][n]])
        im = np.reshape(im, [-1, 1])
        im = np.matmul(im, color)
        im = np.reshape(im, [self.vid.h, self.vid.w, 3])
        return im.astype(np.uint8)

    def _denoise(self, im):
        fil = np.array([[1, 1, 1, 1, 1], [1, 1, 1, 1, 1], [1, 1, 0, 1, 1], [1, 1, 1, 1, 1], [1, 1, 1, 1, 1]]) / 24.
        _, mask = cv2.threshold(im, thresh=1, maxval=255, type=cv2.THRESH_BINARY)
        _, mask = cv2.threshold(cv2.filter2D(mask, -1, fil), thresh=40, maxval=255, type=cv2.THRESH_BINARY)
        im = mask / 255. * im
        return im.astype(np.uint8)


