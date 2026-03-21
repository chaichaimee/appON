# menu.py
import wx
import addonHandler
import tones
import json
import os

addonHandler.initTranslation()
try:
    _ = addonHandler.getTranslation()
except:
    def _(x): return x

_instance = None

class AppOnMenu(wx.Frame):
    def __init__(self, items_func, callback, config_path):
        super(AppOnMenu, self).__init__(None, title=_("AppOnMenu"), size=(400, 500), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
        self.items_func = items_func
        self.callback = callback
        self.config_path = config_path
        self.sort_mode = self.load_config()
        
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        self.list_box = wx.ListBox(panel, style=wx.LB_SINGLE)
        vbox.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(vbox)
        
        self.refresh_list()
        
        self.list_box.Bind(wx.EVT_LISTBOX_DCLICK, self.on_select)
        self.list_box.Bind(wx.EVT_CHAR_HOOK, self.on_key)
        self.list_box.Bind(wx.EVT_CONTEXT_MENU, self.on_context_menu)
        
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.on_timeout, self.timer)
        self.timer.Start(15000)
        
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Show()
        self.Raise()
        self.RequestUserAttention()

    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return json.load(f).get("sort_mode", "alphabet")
            except: pass
        return "alphabet"

    def save_config(self):
        try:
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump({"sort_mode": self.sort_mode}, f)
        except: pass

    def refresh_list(self):
        raw_items = self.items_func(self.sort_mode)
        self.current_items = raw_items
        self.list_box.Clear()
        self.list_box.AppendItems([item[0] for item in raw_items])
        if self.list_box.GetCount() > 0:
            self.list_box.SetSelection(0)
        self.list_box.SetFocus()

    def on_context_menu(self, event):
        m = wx.Menu()
        item_az = m.AppendRadioItem(1, _("Sort A-Z"))
        item_cat = m.AppendRadioItem(2, _("Sort by Category"))
        if self.sort_mode == "alphabet": item_az.Check()
        else: item_cat.Check()
        self.Bind(wx.EVT_MENU, lambda e: self.change_sort("alphabet"), id=1)
        self.Bind(wx.EVT_MENU, lambda e: self.change_sort("category"), id=2)
        self.PopupMenu(m)
        m.Destroy()

    def change_sort(self, mode):
        self.sort_mode = mode
        self.save_config()
        self.refresh_list()
        self.timer.Start(15000)

    def on_select(self, event):
        self.timer.Start(15000)
        idx = self.list_box.GetSelection()
        if idx != wx.NOT_FOUND:
            self.callback(self.current_items[idx][1])

    def on_timeout(self, event):
        tones.beep(100, 100)
        self.Close()

    def on_key(self, event):
        self.timer.Start(15000)
        key = event.GetKeyCode()
        if key == wx.WXK_RETURN: self.on_select(None)
        elif key == wx.WXK_ESCAPE: self.Close()
        else: event.Skip()

    def on_close(self, event):
        global _instance
        _instance = None
        self.Destroy()

def showAppMenu(items_func, callback, config_path):
    global _instance
    if _instance:
        _instance.Raise()
        _instance.RequestUserAttention()
        _instance.timer.Start(15000)
    else:
        _instance = AppOnMenu(items_func, callback, config_path)