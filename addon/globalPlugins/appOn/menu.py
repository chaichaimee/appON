# menu.py

import wx
import addonHandler
import ctypes
from . import configStore

addonHandler.initTranslation()
try:
	_ = addonHandler.getTranslation()
except AttributeError:
	def _(x): return x

_active_instance = None

def _forceForegroundWindow(hwnd):
	# A background process cannot normally steal foreground focus on Windows
	# (foreground lock); attaching input threads with the current foreground
	# window is the standard, documented workaround for a reliable Raise().
	user32 = ctypes.windll.user32
	kernel32 = ctypes.windll.kernel32

	# The triggering gesture holds Alt down (Windows+Alt+A); its eventual
	# key-up can land alone on the window we just focused, which Windows
	# reads as "open the system menu" - the confirmed cause of the System
	# menu (Restore/Move/Size/Minimize/Close) interrupting the reopened menu.
	# A prior attempt "flushed" this by injecting a synthetic Alt down+up of
	# its own, but that IS the exact input pattern that opens the system
	# menu, so it fired every time instead of only sometimes. Pressing and
	# releasing an unrelated modifier (Control) in between breaks Windows'
	# "Alt released alone" detection without itself being that trigger.
	VK_CONTROL = 0x11
	KEYEVENTF_KEYUP = 0x0002
	user32.keybd_event(VK_CONTROL, 0, 0, 0)
	user32.keybd_event(VK_CONTROL, 0, KEYEVENTF_KEYUP, 0)

	foregroundWindow = user32.GetForegroundWindow()
	currentThreadId = kernel32.GetCurrentThreadId()
	foregroundThreadId = user32.GetWindowThreadProcessId(foregroundWindow, None)
	if foregroundThreadId and foregroundThreadId != currentThreadId:
		user32.AttachThreadInput(foregroundThreadId, currentThreadId, True)
		try:
			user32.SetForegroundWindow(hwnd)
		finally:
			user32.AttachThreadInput(foregroundThreadId, currentThreadId, False)
	else:
		user32.SetForegroundWindow(hwnd)

class AppOnMenu(wx.Frame):
	def __init__(self, items_func, callback, on_closed=None, settings_item=None):
		super().__init__(None, title="AppOnMenu", size=(400, 500), style=wx.DEFAULT_FRAME_STYLE | wx.STAY_ON_TOP)
		self.items_func = items_func
		self.callback = callback
		self.on_closed = on_closed
		self.settings_item = settings_item
		self.sort_mode = configStore.loadConfig().get("sort_mode", "alphabet")
		self.cached_raw_items = None

		panel = wx.Panel(self)
		vbox = wx.BoxSizer(wx.VERTICAL)
		self.list_box = wx.ListBox(panel, style=wx.LB_SINGLE)
		vbox.Add(self.list_box, 1, wx.EXPAND | wx.ALL, 10)
		panel.SetSizer(vbox)

		self.refresh_list(use_cache=False)

		self.list_box.Bind(wx.EVT_LISTBOX_DCLICK, self._on_select)
		self.list_box.Bind(wx.EVT_CONTEXT_MENU, self._on_context_menu)
		self.Bind(wx.EVT_CHAR_HOOK, self._on_key)

		self.Bind(wx.EVT_CLOSE, self._on_close)
		self.Show()
		self.bring_to_front()

	def bring_to_front(self):
		self.Raise()
		self.RequestUserAttention()
		try:
			_forceForegroundWindow(self.GetHandle())
		except Exception:
			pass

	def refresh_list(self, use_cache=True):
		if use_cache and self.cached_raw_items is not None:
			raw_items = self.cached_raw_items
		else:
			raw_items = self.items_func("alphabet")
			self.cached_raw_items = raw_items

		sorted_items = self._sort_items(raw_items)
		if self.settings_item:
			sorted_items = sorted_items + [(self.settings_item[0], self.settings_item[1], "9_AppOnSettings")]
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
		configData = configStore.loadConfig()
		configData["sort_mode"] = mode
		configStore.saveConfig(configData)
		self.refresh_list(use_cache=True)

	def _on_select(self, event):
		idx = self.list_box.GetSelection()
		if idx != wx.NOT_FOUND:
			self.callback(self.current_items[idx][1])
			if not self.IsBeingDeleted():
				self.Close()

	def _on_key(self, event):
		key = event.GetKeyCode()
		if key == wx.WXK_RETURN:
			self._on_select(None)
		elif key == wx.WXK_ESCAPE:
			self.Close()
		else:
			event.Skip()

	def _on_close(self, event):
		global _active_instance
		_active_instance = None
		if self.on_closed:
			self.on_closed()
		self.Destroy()

def showAppMenu(items_func, callback, on_closed=None, settings_item=None):
	global _active_instance
	if _active_instance and not _active_instance.IsBeingDeleted():
		_active_instance.bring_to_front()
		return _active_instance
	else:
		_active_instance = AppOnMenu(items_func, callback, on_closed, settings_item=settings_item)
		return _active_instance