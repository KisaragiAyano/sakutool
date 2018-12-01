import wx
import time
import threading


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

        self._render_thread = None
        self.vid = None
        self._is_playing = False
        self._buffer = wx.NullBitmap
        self._fps = 24.

        self._img_woff = None
        self._img_hoff = None

    def load_vid(self, vid):
        self.stop()
        self.vid = vid
        self._img_woff = (self.width - self.vid.w)/2
        self._img_hoff = (self.height - self.vid.h)/2
        self._build_render_thread()
        self._fps = 24.

    def _build_render_thread(self):
        self._render_thread = RenderThread(self._next_frame_render)
        self._render_thread.start()
        self._is_playing = True

    # auto play control
    def play_pause(self):
        if self._render_thread:
            self._is_playing = ~self._is_playing
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
            self._render_thread = None

    def _next_frame_render(self):
        if self.vid and self._is_playing:
            bitmap = self.vid.next_frame()
            self._render_frame(bitmap)

    def switch_fps(self):
        if self.vid and self._render_thread:
            if self._fps == 24.:
                self._fps = 12.
            elif self._fps == 12.:
                self._fps = 6.
            else:
                self._fps = 24.
            self._render_thread.set_fps(self._fps)

    # manual play
    def last_frame(self):
        if self.vid:
            self.pause()
            bitmap = self.vid.last_frame()
            self._render_frame(bitmap)

    def next_frame(self):
        if self.vid:
            self.pause()
            bitmap = self.vid.next_frame()
            self._render_frame(bitmap)

    def cur_frame(self):
        if self.vid:
            self.pause()
            bitmap = self.vid.cur_frame()
            self._render_frame(bitmap)

    def _render_frame(self, bitmap):
        dc = wx.BufferedDC(wx.ClientDC(self), self._buffer)
        # dc.Clear()
        dc.DrawBitmap(bitmap, self._img_woff, self._img_hoff)
        self.refresh_info()

    def refresh_info(self):
        info_str = ' Playing Info \n\n'
        info_str += 'FPS of playing: {}\n'.format(self._fps)
        if self.vid:
            info_str += 'No. of frames: {}/{}\n'.format(self.vid.cur_frame_index, self.vid.vid_frames)
        else:
            pass
        self.ext_print(info_str)
