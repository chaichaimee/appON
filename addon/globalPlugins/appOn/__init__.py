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
import winUser

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

	def terminate(self):
		detectors.unregister_cache_listener(self._on_cache_updated)
		self._active_menu = None
		super().terminate()

	def _on_cache_updated(self):
		if not self._active_menu or hasattr(self._active_menu, 'IsBeingDeleted') and self._active_menu.IsBeingDeleted():
			return
		if hasattr(self._active_menu, 'refresh_list'):
			wx.CallAfter(self._safe_refresh_menu)

	def _safe_refresh_menu(self):
		if not self._active_menu or self._active_menu.IsBeingDeleted():
			return
		try:
			self._active_menu.refresh_list(use_cache=True)
		except Exception:
			pass

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		try:
			if obj.role != Role.LISTITEM:
				return
		except Exception:
			return

		# Use window handle to check parent window title efficiently
		try:
			hwnd = obj.windowHandle
			if hwnd and winUser.getWindowText(hwnd) == "AppOnMenu":
				clsList.insert(0, NoPositionListItem)
		except Exception:
			pass

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
				category = detectors._get_category(key)
				result.append((label, method, category))
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
		def create_menu():
			self._active_menu = menu.showAppMenu(
				self._getAvailableAppItems,
				lambda cb: cb(None),
				self.CONFIG_PATH,
				on_closed=on_menu_closed
			)
		wx.CallAfter(create_menu)
	script_showAppMenu.__doc__ = _("Shows the appOn menu with all available applications")
	script_showAppMenu.category = "appOn"

	def script_launchAudacity(self, gesture):
		self._launchByKey("audacity")
	script_launchAudacity.__doc__ = _("Launches Audacity application")
	script_launchAudacity.category = "appOn"

	def script_launchBrave(self, gesture):
		self._launchByKey("brave")
	script_launchBrave.__doc__ = _("Launches Brave web browser")
	script_launchBrave.category = "appOn"

	def script_launchChrome(self, gesture):
		self._launchByKey("chrome")
	script_launchChrome.__doc__ = _("Launches Google Chrome web browser")
	script_launchChrome.category = "appOn"

	def script_launchCmd(self, gesture):
		self._launchByKey("cmd", True)
	script_launchCmd.__doc__ = _("Launches Command Prompt")
	script_launchCmd.category = "appOn"

	def script_launchControlPanel(self, gesture):
		self._launchByKey("controlpanel")
	script_launchControlPanel.__doc__ = _("Opens Windows Control Panel")
	script_launchControlPanel.category = "appOn"

	def script_launchDiskCleanup(self, gesture):
		self._launchByKey("diskcleanup")
	script_launchDiskCleanup.__doc__ = _("Launches Windows Disk Cleanup utility")
	script_launchDiskCleanup.category = "appOn"

	def script_launchEdge(self, gesture):
		self._launchByKey("edge")
	script_launchEdge.__doc__ = _("Launches Microsoft Edge web browser")
	script_launchEdge.category = "appOn"

	def script_launchEverything(self, gesture):
		self._launchByKey("everything")
	script_launchEverything.__doc__ = _("Launches Everything search utility")
	script_launchEverything.category = "appOn"

	def script_launchFirefox(self, gesture):
		self._launchByKey("firefox")
	script_launchFirefox.__doc__ = _("Launches Mozilla Firefox web browser")
	script_launchFirefox.category = "appOn"

	def script_launchGitHubDesktop(self, gesture):
		self._launchByKey("githubdesktop")
	script_launchGitHubDesktop.__doc__ = _("Launches GitHub Desktop application")
	script_launchGitHubDesktop.category = "appOn"

	def script_launchExcel(self, gesture):
		self._launchByKey("excel")
	script_launchExcel.__doc__ = _("Launches Microsoft Excel")
	script_launchExcel.category = "appOn"

	def script_launchPowerPoint(self, gesture):
		self._launchByKey("powerpoint")
	script_launchPowerPoint.__doc__ = _("Launches Microsoft PowerPoint")
	script_launchPowerPoint.category = "appOn"

	def script_launchMSWord(self, gesture):
		self._launchByKey("word")
	script_launchMSWord.__doc__ = _("Launches Microsoft Word")
	script_launchMSWord.category = "appOn"

	def script_launchNotepad(self, gesture):
		self._launchByKey("notepad")
	script_launchNotepad.__doc__ = _("Launches Windows Notepad")
	script_launchNotepad.category = "appOn"

	def script_launchNotepadPlusPlus(self, gesture):
		self._launchByKey("notepadpp")
	script_launchNotepadPlusPlus.__doc__ = _("Launches Notepad++ editor")
	script_launchNotepadPlusPlus.category = "appOn"

	def script_launchPowershell(self, gesture):
		self._launchByKey("powershell", True)
	script_launchPowershell.__doc__ = _("Launches Windows PowerShell")
	script_launchPowershell.category = "appOn"

	def script_launchReaper(self, gesture):
		self._launchByKey("reaper")
	script_launchReaper.__doc__ = _("Launches REAPER audio software")
	script_launchReaper.category = "appOn"

	def script_launchRegedit(self, gesture):
		self._launchByKey("regedit", True)
	script_launchRegedit.__doc__ = _("Opens Windows Registry Editor")
	script_launchRegedit.category = "appOn"

	def script_launchThisPC(self, gesture):
		self._launchByKey("thispc")
	script_launchThisPC.__doc__ = _("Opens This PC file explorer")
	script_launchThisPC.category = "appOn"

	def script_launchWinamp(self, gesture):
		self._launchByKey("winamp")
	script_launchWinamp.__doc__ = _("Launches Winamp media player")
	script_launchWinamp.category = "appOn"

	def script_launchDefender(self, gesture):
		self._launchByKey("defender")
	script_launchDefender.__doc__ = _("Opens Windows Security settings")
	script_launchDefender.category = "appOn"

	def script_launchWordPad(self, gesture):
		self._launchByKey("wordpad")
	script_launchWordPad.__doc__ = _("Launches Windows WordPad")
	script_launchWordPad.category = "appOn"

	def script_launchGoogleDrive(self, gesture):
		self._launchByKey("googledrive")
	script_launchGoogleDrive.__doc__ = _("Launches Google Drive for Desktop")
	script_launchGoogleDrive.category = "appOn"

	__gestures = {"kb:alt+windows+a": "showAppMenu"}