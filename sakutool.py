import wx

from sakuvid import SakuVid, VidNotFoundError, VidFile
from booruinfo import BooruInfoPanel
import cmdline
import utils
from renderer import Renderer
from timeline import TimelinePanel


class SakutoolApp(wx.App):
    def OnInit(self):
        self.frame = SakutoolFrame()
        self.SetTopWindow(self.frame)
        self.frame.Show()
        return True


class SakutoolFrame(wx.Frame):
    def __init__(self):
        configer = utils.Configer()
        self.path = configer.get_asset_path()

        # --- init GUI ---
        self.size = size = wx.Size(1024, 960)
        self.width, self.height = size.GetWidth(), size.GetHeight()
        style = wx.NO_BORDER | wx.TRANSPARENT_WINDOW #| wx.CAPTION | wx.CLOSE_BOX | wx.MINIMIZE_BOX
        wx.Frame.__init__(self, parent=None, title='Sakutool v0.2 -- Niku.KK',
                          pos=wx.DefaultPosition, size=size,
                          style=style)
        self.Centre()
        self.SetCanFocus(False)

        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour(utils.BG_DARK)
        # self.panel.SetFocusIgnoringChildren()

        sizer = wx.GridBagSizer(0, 5)

        image_height = self.width*9//16
        self.renderer = Renderer(self.panel, self._pring_play_info, size=(self.width, image_height))

        self.timeline_panel = TimelinePanel(self.panel, size=(self.width, 80))

        info_height = self.height - image_height - 80 - 20 - 5
        self.cmd_panel = cmdline.CmdPanel(self.panel, self._print_status_bar, size=(200, info_height))
        self.booru_panel = BooruInfoPanel(self.panel, size=(200, info_height))
        self.info_play = wx.StaticText(self.panel, size=(300, info_height), label=' Playing Info \n\n')
        self.info_play.SetForegroundColour(utils.FG_LIGHT)
        self.info_play.SetFont(wx.Font(9, family=wx.FONTFAMILY_MODERN,
                                       style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL))

        self.status_bar = wx.StaticText(self.panel, size=(self.width, 20))
        self.status_bar.SetBackgroundColour('black')
        self.status_bar.SetForegroundColour(utils.FG_LIGHT)
        self.status_bar.SetFont(wx.Font(9, family=wx.FONTFAMILY_MODERN,
                                        style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL))

        sizer.Add(self.renderer, pos=(0, 0), span=(1, 3), flag=wx.ALL, border=0)
        sizer.Add(self.timeline_panel, pos=(1, 0), span=(1, 3), flag=wx.BOTTOM, border=5)
        sizer.Add(self.cmd_panel, pos=(2, 0), flag=wx.ALL | wx.ALIGN_BOTTOM, border=0)
        sizer.Add(self.booru_panel, pos=(2, 1), flag=wx.LEFT | wx.EXPAND, border=5)
        sizer.Add(self.info_play, pos=(2, 2), flag=wx.LEFT | wx.EXPAND, border=5)
        sizer.Add(self.status_bar, pos=(3, 0), span=(1, 3), flag=wx.ALL, border=0)

        self._bind_all()
        # self.timer = wx.Timer(self)
        # self.Bind(wx.EVT_TIMER, self._ontimer, self.timer)

        # --- data
        # self.path = './asset/'
        self.vid = None
        self._is_loading = False

        self._mouse_focus = None

        self.panel.SetSizerAndFit(sizer)
        self.build_cmd_panel()
        self._booru_panel_refresh()

    def _onkeydown(self, event):
        keycode = event.GetKeyCode()
        shiftdown = event.ShiftDown()
        keycode = cmdline.reformat(keycode, shiftdown)
        if not self._is_loading:
            name, opt = self.cmd_panel.operate(keycode)
            if name == 'booru input':
                booru_ids = utils.search(self.path, opt)
                if len(booru_ids) > 10:
                    booru_ids = booru_ids[:10]
                info = ''
                if booru_ids:
                    info = '  Local vids:\n    ' + '\n    '.join(booru_ids)
                self.cmd_panel.add_info(info)

    def _onmouse(self, event):
        if event.ButtonDown():
            pass
        elif event.Dragging():
            if self._mouse_focus == self.timeline_panel.progress_panel:
                self.__seek()
        elif event.ButtonUp():
            if self._mouse_focus == self.timeline_panel.progress_panel:
                self.renderer.resume()
            self._mouse_focus = None

    def _onmouse_drag(self, event):
        if event.ButtonDown():
            self._mouse_focus = self.status_bar
            self._drag_pos = event.GetPosition()
        elif event.Dragging() and self._mouse_focus == self.status_bar:
            cur_pos = event.GetPosition()
            frame_pos = self.GetPosition()
            pos = (frame_pos[0] + cur_pos[0] - self._drag_pos[0], frame_pos[1] + cur_pos[1] - self._drag_pos[1])
            self.SetPosition(pos)
        elif event.ButtonUp():
            self._mouse_focus = None

    def _onmouse_seek(self, event):
        if event.ButtonDown():
            self._mouse_focus = self.timeline_panel.progress_panel
            self.__seek()
        elif event.Dragging() and self._mouse_focus == self.timeline_panel.progress_panel:
            self.__seek()
        elif event.ButtonUp():
            if self._mouse_focus == self.timeline_panel.progress_panel:
                self.renderer.resume()
            self._mouse_focus = None

    def __seek(self):
        if self.vid:
            x = self.ScreenToClient(wx.GetMousePosition())[0]
            p = x / self.timeline_panel.width
            self.timeline_panel.set_progress(p)
            self.renderer.seek(p)

    # handlers
    def _pring_play_info(self, info_str, info):
        self.info_play.SetLabel(info_str)
        progress = info['cur_frame_index']/info['num_frames']
        self.timeline_panel.set_progress(progress)

    def _print_status_bar(self, s):
        # self.SetStatusText(s)
        self.status_bar.SetLabel(s)

    # --- ---
    def _open_file(self):
        files_filter = "Video (*.mp4;*.avi;*.webm)|*.mp4;*.avi;*.webm"
        file_dialog = wx.FileDialog(self, message="", wildcard=files_filter, style=wx.FD_OPEN)
        if file_dialog.ShowModal() != wx.ID_OK:
            return
        vid_path = file_dialog.GetPaths()[0]

        self.renderer.pause()
        self.vid = VidFile(vid_path)
        self.renderer.load_vid(self.vid)
        return True

    def _load_vid(self, booru_id):
        self.renderer.pause()
        flag = False
        try:
            self._is_loading = True
            self._print_status_bar('  L o a d i n g ...')
            self.vid = SakuVid(booru_id, self.path, maxsize=self.renderer.size)
            self._is_loading = False
            self.booru_id = booru_id

            self.renderer.stop()
            self.renderer.load_vid(self.vid)
            self._booru_panel_refresh()
            flag = True

        except VidNotFoundError:
            self._is_loading = False
            print('Booru ID Not Found..')

        return flag

    def _booru_panel_refresh(self):
        if self.vid:
            self.booru_panel.update(info=self.vid.booru_info)

    # --- save
    def save_image(self):
        if self.vid:
            self.renderer.pause()
            self.vid.save_frame()
            self.renderer.next_frame()

    # build menu
    def build_cmd_panel(self):
        cmd_menu_root = self.cmd_panel.menu_root
        cmd_menu_booru_input = cmdline.CmdInput(parent=cmd_menu_root, name='booru input',
                                                func=self._load_vid, allow=cmdline.is_num)

        cmd_menu_root.new_menu_item(name='open booru vid', key='i', ptr=cmd_menu_booru_input, helpdoc='input id.')
        cmd_menu_root.new_func_item(name='open video', key='I', ptr=self._open_file, helpdoc='open video file.')
        cmd_menu_root.new_func_item(name='play/stop', key=' ', ptr=self.renderer.play_pause)
        cmd_menu_root.new_func_item(name='last frame', key='j', ptr=self.renderer.last_frame)
        cmd_menu_root.new_func_item(name='next frame', key='k', ptr=self.renderer.next_frame)
        cmd_menu_root.new_func_item(name='switch fps', key='f', ptr=self.renderer.switch_fps, helpdoc='1x/0.5x/0.25x')
        cmd_menu_root.new_func_item(name='canny   ', key='c', ptr=self.renderer.switch_canny, helpdoc='')
        cmd_menu_root.new_func_item(name='switch k', key='m', ptr=self.renderer.switch_k, helpdoc='1/2/3')
        cmd_menu_root.new_func_item(name='switch onion', key='o', ptr=self.renderer.switch_onion, helpdoc='0/1/2/3')
        cmd_menu_root.new_func_item(name='switch grid', key='g', ptr=self.renderer.switch_grid, helpdoc='')
        cmd_menu_root.new_func_item(name='save jpg', key='s', ptr=self.save_image, helpdoc='...')
        cmd_menu_root.new_func_item(name='exit', key='q', ptr=self.exit)

        self.cmd_panel.refresh_info()
        return

    def _bind_all(self):
        self.Bind(wx.EVT_KEY_DOWN, self._onkeydown)
        self.panel.Bind(wx.EVT_KEY_DOWN, self._onkeydown)
        self.panel.Bind(wx.EVT_MOUSE_EVENTS, self._onmouse)

        self.renderer.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.renderer.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        self.timeline_panel.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.timeline_panel.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        self.timeline_panel.progress_panel.Bind(wx.EVT_MOUSE_EVENTS, self._onmouse_seek)
        self.cmd_panel.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.cmd_panel.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        self.booru_panel.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.booru_panel.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        self.info_play.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.info_play.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)
        self.status_bar.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.status_bar.Bind(wx.EVT_MOUSE_EVENTS, self._onmouse_drag)

    def exit(self):
        self.renderer.stop()
        wx.Exit()


if __name__ == '__main__':
    app = SakutoolApp(False)
    app.MainLoop()

