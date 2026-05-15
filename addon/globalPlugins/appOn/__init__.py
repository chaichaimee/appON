# __init__.py
# Copyright (C) 2026 Chai Chaimee
# Licensed under GNU General Public License. See COPYING.txt for details.

import globalPluginHandler
import ui
import addonHandler
import wx
import os
import globalVars
from . import detectors
from . import menu
from NVDAObjects import NVDAObject
from controlTypes import Role

addonHandler.initTranslation()
try:
	_ = addonHandler.getTranslation()
except:
	def _(x): return x

class NoPositionListItem(NVDAObject):
	def _get_positionInfo(self):
		return {}

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = "appOn"
	CONFIG_PATH = os.path.join(globalVars.appArgs.configPath, "ChaiChaimee", "appOn.json")

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		detectors.start_cache_refresh()
		detectors.register_cache_listener(self._on_cache_updated)
		self._active_menu = None

	def _on_cache_updated(self):
		if self._active_menu and hasattr(self._active_menu, 'refresh_list'):
			wx.CallAfter(self._active_menu.refresh_list, use_cache=True)

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role != Role.LISTITEM:
			return
		parent = obj.parent
		while parent:
			if parent.role == Role.WINDOW and parent.name == _("AppOnMenu"):
				clsList.insert(0, NoPositionListItem)
				return
			parent = parent.parent

	def _getAvailableAppItems(self, sortMode="alphabet"):
		cachedItems = detectors.get_cached_app_items(sortMode)
		appMethodMap = {
			"audacity": self.script_launchAudacity, "brave": self.script_launchBrave,
			"chrome": self.script_launchChrome, "cmd": self.script_launchCmd,
			"controlpanel": self.script_launchControlPanel, "diskcleanup": self.script_launchDiskCleanup,
			"edge": self.script_launchEdge, "everything": self.script_launchEverything,
			"firefox": self.script_launchFirefox, "githubdesktop": self.script_launchGitHubDesktop,
			"excel": self.script_launchExcel, "powerpoint": self.script_launchPowerPoint,
			"word": self.script_launchMSWord, "notepad": self.script_launchNotepad,
			"notepadpp": self.script_launchNotepadPlusPlus, "powershell": self.script_launchPowershell,
			"reaper": self.script_launchReaper, "regedit": self.script_launchRegedit,
			"thispc": self.script_launchThisPC, "winamp": self.script_launchWinamp,
			"defender": self.script_launchDefender, "wordpad": self.script_launchWordPad,
			"googledrive": self.script_launchGoogleDrive,
		}
		result = []
		for label, key, _ in cachedItems:
			method = appMethodMap.get(key)
			if method:
				result.append((label, method))
		return result

	def _launchByKey(self, key, requireAdmin=False):
		if key == "defender":
			paths = next((p for k, n, p in detectors.APP_DEFINITIONS if k == key), [])
			exePath = detectors.find_exe(paths)
			if exePath:
				try:
					os.startfile(exePath)
				except Exception as err:
					ui.message(_("Error: {error}").format(error=str(err)))
			else:
				try:
					import ctypes
					ctypes.windll.shell32.ShellExecuteW(None, "open", "windowsdefender://Threatsettings", None, None, 1)
				except Exception as err:
					ui.message(_("Error opening Windows Security: {error}").format(error=str(err)))
			return

		paths = next((p for k, n, p in detectors.APP_DEFINITIONS if k == key), [])
		exePath = detectors.find_exe(paths)
		if not exePath:
			exePath = paths[0] if paths else key
		try:
			if requireAdmin:
				import ctypes
				ctypes.windll.shell32.ShellExecuteW(None, "runas", exePath, None, None, 1)
			else:
				os.startfile(os.path.expandvars(exePath))
		except Exception as err:
			ui.message(_("Error: {error}").format(error=str(err)))

	def script_showAppMenu(self, gesture):
		def on_menu_closed():
			self._active_menu = None
		wx.CallAfter(lambda: setattr(self, '_active_menu', menu.showAppMenu(
			self._getAvailableAppItems,
			lambda cb: cb(None),
			self.CONFIG_PATH,
			on_closed=on_menu_closed
		)))
	script_showAppMenu.category = "appOn"
	script_showAppMenu.__doc__ = _("Shows the appOn menu.")

	script_launchAudacity = lambda self, g: self._launchByKey("audacity")
	script_launchBrave = lambda self, g: self._launchByKey("brave")
	script_launchChrome = lambda self, g: self._launchByKey("chrome")
	script_launchCmd = lambda self, g: self._launchByKey("cmd", True)
	script_launchControlPanel = lambda self, g: self._launchByKey("controlpanel")
	script_launchDiskCleanup = lambda self, g: self._launchByKey("diskcleanup")
	script_launchEdge = lambda self, g: self._launchByKey("edge")
	script_launchEverything = lambda self, g: self._launchByKey("everything")
	script_launchFirefox = lambda self, g: self._launchByKey("firefox")
	script_launchGitHubDesktop = lambda self, g: self._launchByKey("githubdesktop")
	script_launchExcel = lambda self, g: self._launchByKey("excel")
	script_launchPowerPoint = lambda self, g: self._launchByKey("powerpoint")
	script_launchMSWord = lambda self, g: self._launchByKey("word")
	script_launchNotepad = lambda self, g: self._launchByKey("notepad")
	script_launchNotepadPlusPlus = lambda self, g: self._launchByKey("notepadpp")
	script_launchPowershell = lambda self, g: self._launchByKey("powershell", True)
	script_launchReaper = lambda self, g: self._launchByKey("reaper")
	script_launchRegedit = lambda self, g: self._launchByKey("regedit", True)
	script_launchThisPC = lambda self, g: self._launchByKey("thispc")
	script_launchWinamp = lambda self, g: self._launchByKey("winamp")
	script_launchDefender = lambda self, g: self._launchByKey("defender")
	script_launchWordPad = lambda self, g: self._launchByKey("wordpad")
	script_launchGoogleDrive = lambda self, g: self._launchByKey("googledrive")

	for name in list(locals().keys()):
		if name.startswith("script_launch"):
			item = locals()[name]
			if callable(item):
				item.category = "appOn"

	__gestures = {"kb:alt+windows+a": "showAppMenu"}