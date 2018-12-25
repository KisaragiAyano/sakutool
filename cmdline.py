import wx
import utils


class OptType:
    NULL = 0  # no refresh
    FUNC = 1  # no refresh
    MENU = 2  # menu changed, need refresh
    INPUT = 3  # refresh


class CmdPanel(wx.Panel):
    def __init__(self, parent, ext_print, size=(200, 400)):
        self.size = size
        self.width, self.height = size
        self.ext_print = ext_print
        wx.Panel.__init__(self, parent, size=size)

        self.menu_root = CmdMenu(None, name='root')
        self.menu_ptr = self.menu_root

        self.cmds_list_text = wx.StaticText(self, size=size)
        self.cmds_list_text.SetBackgroundColour('black')
        self.cmds_list_text.SetForegroundColour(utils.LIGHT_GRAY)
        self.cmds_list_text.SetFont(wx.Font(9, family=wx.FONTFAMILY_MODERN,
                                            style=wx.FONTSTYLE_NORMAL, weight=wx.FONTWEIGHT_NORMAL))
        self.cmds_list_text.Bind(wx.EVT_KEY_DOWN, utils.event_skip)
        self.cmds_list_text.Bind(wx.EVT_MOUSE_EVENTS, utils.event_skip)

        self._ext_input = ''

        self.mode = 0

    def operate(self, key, mode=0):
        self.mode = mode
        self.menu_ptr, opt_type = self.menu_ptr.operate(key, mode)
        if opt_type in [OptType.MENU, OptType.INPUT]:
            self.refresh_info(self.mode)
        return self.menu_ptr.name, self.menu_ptr.opt

    def add_info(self, s, mode=0):
        self._ext_input = s
        self.refresh_info(mode)

    def refresh_info(self, mode=0):
        cmds_input = self.get_tree_info(mode) + to_string(self.menu_ptr.opt) + '_'
        self.ext_print(cmds_input)

        cmds_list = '\n Command : name, Comment\n\n' + self.get_leaf_info(mode)
        cmds_list += self._ext_input
        self.cmds_list_text.SetLabel(cmds_list)
        self.resize_cmds_list(cmds_list.count('\n'))
        self._ext_input = ''

    def get_tree_info(self, mode=0):
        strings = []
        ptr = self.menu_ptr.parent
        while ptr:
            key = ptr.opt
            name, helpdoc = ptr.get_item_info(key, mode)
            strings.append('{}({})>'.format(to_string(key), name))
            ptr = ptr.parent
        return ' '.join(reversed(strings))

    def get_leaf_info(self, mode=0):
        info = ''
        ptr = self.menu_ptr
        lines = []
        for key in ptr.items(mode):
            name, helpdoc = ptr.get_item_info(key, mode)
            lines.append('  {} : {}, {}'.format(to_string(key), name, helpdoc))
        if lines:
            info = '\n'.join(lines)
        return info

    def resize_cmds_list(self, rows):
        dh = rows * 12 + 15
        self.cmds_list_text.SetPosition((0, self.height - dh))


class CmdMenu(object):
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        # self.items = items
        self.mode_items = {0: {}}
        self.opt = None

        self.helpdoc = ''

    def items(self, mode=0):
        if mode in self.mode_items:
            return self.mode_items[mode]
        else:
            return {}

    def operate(self, key, mode=0):
        items = self.items(mode)
        if is_esc(key):
            self.esc()
            if self.parent:
                return self.parent.operate(key)[0], OptType.MENU
            else:
                return self, OptType.NULL     # trace back to root menu
        elif is_back(key):
            self.back()
            if self.parent:
                self.parent.back()
                return self.parent, OptType.MENU
            else:
                return self, OptType.NULL
        elif is_text(key):
            if key in items:
                item = items[key]
                if isinstance(item, CmdFuncItem):
                    self.opt = None
                    ptr = item()
                    return ptr, OptType.FUNC
                elif isinstance(item, CmdMenuItem):
                    self.opt = key
                    ptr = item()
                    return ptr, OptType.MENU
        return self, OptType.NULL

    def esc(self):
        self.opt = None
    def back(self):
        self.opt = None

    def add_item(self, item, mode=0):
        if isinstance(mode, int):
            mode = [mode]
        for m in mode:
            if m not in self.mode_items:
                self.mode_items[m] = {}
            self.mode_items[m][item.key] = item
    def new_menu_item(self, name, key, ptr, mode=0, helpdoc='...'):
        item = CmdMenuItem(self, name, key, ptr, helpdoc=helpdoc)
        self.add_item(item, mode)
    def new_func_item(self, name, key, ptr, mode=0, helpdoc='...'):
        item = CmdFuncItem(self, name, key, ptr, helpdoc=helpdoc)
        self.add_item(item, mode)

    def get_item_info(self, key, mode=0):
        items = self.items(mode)
        if key in items:
            item = items[key]
            return item.name, item.helpdoc


class CmdInput(object):
    def __init__(self, parent, name, func, allow=None, min_len=1, max_len=5):
        assert parent
        self.parent = parent
        self.name = name
        self.func = func
        self.allow = is_num if not allow else allow
        self.min_len = min_len
        self.max_len = max_len

        self.mode_items = {0: {}}
        self.opt = ''
        self.helpdoc = ''

    def items(self, mode=0):
        if mode in self.mode_items:
            return self.mode_items[mode]
        else:
            return {}

    def operate(self, key, mode=0):
        if is_esc(key):
            self.esc()
            self.parent.esc()
            return self.parent, OptType.MENU
        elif is_back(key):
            if self.opt:
                self.back()
                return self, OptType.INPUT
            else:
                return self, OptType.NULL
        elif is_space(key):
            if len(self.opt) < self.min_len:
                return self, OptType.NULL
            res = self.func(self.opt)
            if res:
                self.parent.back()
                self.esc()
                return self.parent, OptType.MENU
            else:
                self.opt = ''
                return self, OptType.INPUT
        elif self.allow(key):
            if len(self.opt) < self.max_len:
                self.opt += to_string(key)
                return self, OptType.INPUT
            else:
                return self, OptType.NULL
        return self, OptType.NULL

    def esc(self):
        self.opt = ''
    def back(self):
        if self.opt:
            self.opt = self.opt[:-1]

    def get_item_info(self, key, mode=0):
        return '', ''


class CmdItem(object):
    def __init__(self, parent, name, key, ptr, helpdoc='...'):
        self.parent = parent
        self.name = name
        if isinstance(key, str):
            self.key = ord(key)
        self.ptr = ptr
        # self.mode_ptr = {0: ptr}
        self.helpdoc = helpdoc
class CmdMenuItem(CmdItem):
    def __call__(self):
        # key = args[0]
        # if key == self.key:
        #     return self.ptr
        # return False
        # ptr = self.mode_ptr[mode]
        ptr = self.ptr
        return ptr
class CmdFuncItem(CmdItem):
    def __call__(self):
        # key = args[0]
        # if key == self.key:
        #     self.ptr()
        #     return True
        # return False
        # ptr = self.mode_ptr[mode]
        ptr = self.ptr
        ptr()
        return self.parent


# TODO
def to_string(key):
    if isinstance(key, str):
        return key
    elif key == None:
        return ''
    elif is_text(key):
        return chr(key)
    elif key == wx.WXK_LEFT:
        return 'left'
    elif key == wx.WXK_RIGHT:
        return 'right'
    elif key == wx.WXK_UP:
        return 'up'
    elif key == wx.WXK_DOWN:
        return 'down'
    else:
        return '?'

def reformat(key, shift=False):
    if 323 < key < 334:
        key -= 276
    elif 64 < key < 91 and not shift:
        key += 32
    return key

def is_back(key):
    return key == wx.WXK_BACK

def is_esc(key):
    return key == wx.WXK_ESCAPE

def is_space(key):
    return key == wx.WXK_SPACE

def is_alpha(key):
    return 64 < key < 91 or 96 < key < 123

def is_num(key):
    return 47 < key < 58 or 323 < key < 334

def is_text(key):
    return 31 < key < 127