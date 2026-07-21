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

_active_instance = None

class AppOnMenu(wx.Frame):
	def __init__(self, items_func, callback, config_path, on_closed=None):
		super().__init__(None, title="AppOnMenu", size=(400, 500), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.items_func = items_func
		self.callback = callback
		self.config_path = config_path
		self.on_closed = on_closed
		self.sort_mode = self._load_config()
		self.cached_raw_items = None

		panel = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)
		self.list_box = wx.ListBox(panel, style=wx.LB_SINGLE)
		vbox.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 10)
		panel.SetSizer(vbox)

		self.refresh_list(use_cache=False)

		self.list_box.Bind(wx.EVT_LISTBOX_DCLICK, self._on_select)
		self.list_box.Bind(wx.EVT_CHAR_HOOK, self._on_key)
		self.list_box.Bind(wx.EVT_CONTEXT_MENU, self._on_context_menu)

		self.timer = wx.Timer(self)
		self.Bind(wx.EVT_TIMER, self._on_timeout, self.timer)
		self.timer.Start(15000)

		self.Bind(wx.EVT_CLOSE, self._on_close)
		self.Show()
		self.Raise()
		self.RequestUserAttention()

	def _load_config(self):
		if os.path.exists(self.config_path):
			try:
				with open(self.config_path, 'r', encoding='utf-8') as f:
					return json.load(f).get("sort_mode", "alphabet")
			except Exception:
				pass
		return "alphabet"

	def _save_config(self):
		try:
			os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
			with open(self.config_path, 'w', encoding='utf-8') as f:
				json.dump({"sort_mode": self.sort_mode}, f)
		except Exception:
			pass

	def refresh_list(self, use_cache=True):
		if use_cache and self.cached_raw_items is not None:
			raw_items = self.cached_raw_items
		else:
			raw_items = self.items_func("alphabet")
			self.cached_raw_items = raw_items

		sorted_items = self._sort_items(raw_items)
		self.current_items = sorted_items
		self.list_box.Clear()
		self.list_box.AppendItems([item[0] for item in sorted_items])
		if self.list_box.GetCount() > 0:
			self.list_box.SetSelection(0)
		self.list_box.SetFocus()

	def _sort_items(self, items):
		# items are tuples of (label, method, category)
		if self.sort_mode == "category":
			return sorted(items, key=lambda x: (x[2] if len(x) > 2 else "7_Others", x[0].lower()))
		else:
			return sorted(items, key=lambda x: x[0].lower())

	def _on_context_menu(self, event):
		menu = wx.Menu()
		item_az = menu.AppendRadioItem(1, _("Sort A-Z"))
		item_cat = menu.AppendRadioItem(2, _("Sort by Category"))
		if self.sort_mode == "alphabet":
			item_az.Check()
		else:
			item_cat.Check()
		self.Bind(wx.EVT_MENU, lambda e: self._change_sort("alphabet"), id=1)
		self.Bind(wx.EVT_MENU, lambda e: self._change_sort("category"), id=2)
		self.PopupMenu(menu)
		menu.Destroy()

	def _change_sort(self, mode):
		self.sort_mode = mode
		self._save_config()
		self.refresh_list(use_cache=True)
		self.timer.Start(15000)

	def _on_select(self, event):
		self.timer.Start(15000)
		idx = self.list_box.GetSelection()
		if idx != wx.NOT_FOUND:
			self.callback(self.current_items[idx][1])

	def _on_timeout(self, event):
		tones.beep(100, 100)
		self.Close()

	def _on_key(self, event):
		self.timer.Start(15000)
		key = event.GetKeyCode()
		if key == wx.WXK_RETURN:
			self._on_select(None)
		elif key == wx.WXK_ESCAPE:
			self.Close()
		else:
			event.Skip()

	def _on_close(self, event):
		global _active_instance
		if self.timer:
			self.timer.Stop()
		_active_instance = None
		if self.on_closed:
			self.on_closed()
		self.Destroy()

def showAppMenu(items_func, callback, config_path, on_closed=None):
	global _active_instance
	if _active_instance and not _active_instance.IsBeingDeleted():
		_active_instance.Raise()
		_active_instance.RequestUserAttention()
		_active_instance.timer.Start(15000)
		return _active_instance
	else:
		_active_instance = AppOnMenu(items_func, callback, config_path, on_closed)
		return _active_instance