# __init__.py
# Copyright (C) 2026 Chai Chaimee
# Licensed under GNU General Public License. See COPYING.txt for details.

import globalPluginHandler
import ui
import addonHandler
import wx
import os
from . import detectors
from . import menu
from . import configStore
from NVDAObjects import NVDAObject
from controlTypes import Role
import winUser

addonHandler.initTranslation()
try:
	_ = addonHandler.getTranslation()
except AttributeError:
	def _(x): return x

class NoPositionListItem(NVDAObject):
	def _get_positionInfo(self):
		return {}

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = "appOn"

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		detectors.start_cache_refresh()
		detectors.register_cache_listener(self._on_cache_updated)
		self._active_menu = None

	def terminate(self):
		detectors.unregister_cache_listener(self._on_cache_updated)
		detectors.shutdown_cache()
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
		disabledKeys = set(configStore.loadConfig().get("disabled_apps", []))
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
			"googledrive": self.script_launchGoogleDrive, "vscode": self.script_launchVSCode,
			"git": self.script_launchGit, "libreofficecalc": self.script_launchLibreOfficeCalc,
			"libreofficedraw": self.script_launchLibreOfficeDraw, "libreofficeimpress": self.script_launchLibreOfficeImpress,
			"libreofficemath": self.script_launchLibreOfficeMath, "libreofficewriter": self.script_launchLibreOfficeWriter,
		}
		result = []
		for label, key, _ in cachedItems:
			if key in disabledKeys:
				continue
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
				on_closed=on_menu_closed,
				settings_item=(_("AppOn Setting"), self._openAppOnSettings)
			)
		wx.CallAfter(create_menu)
	script_showAppMenu.__doc__ = _("Shows the appOn menu with all available applications")
	script_showAppMenu.category = "appOn"

	def _openAppOnSettings(self, gesture):
		# The menu now closes itself right after any selection (see
		# AppOnMenu._on_select), so no explicit Close() is needed here -
		# calling it again on an already-closing frame risked a double
		# Close()/Destroy() sequence.
		wx.CallAfter(self._showSettingsDialog)

	def _showSettingsDialog(self):
		from . import settingsDialog
		settingsDialog.showSettingsDialog(detectors.APP_DEFINITIONS)

	def script_launchAudacity(self, gesture):
		self._launchByKey("audacity")
	script_launchAudacity.__doc__ = _("Audacity")
	script_launchAudacity.category = "appOn"

	def script_launchBrave(self, gesture):
		self._launchByKey("brave")
	script_launchBrave.__doc__ = _("Brave")
	script_launchBrave.category = "appOn"

	def script_launchChrome(self, gesture):
		self._launchByKey("chrome")
	script_launchChrome.__doc__ = _("Google Chrome")
	script_launchChrome.category = "appOn"

	def script_launchCmd(self, gesture):
		self._launchByKey("cmd", True)
	script_launchCmd.__doc__ = _("Command Prompt")
	script_launchCmd.category = "appOn"

	def script_launchControlPanel(self, gesture):
		self._launchByKey("controlpanel")
	script_launchControlPanel.__doc__ = _("Control Panel")
	script_launchControlPanel.category = "appOn"

	def script_launchDiskCleanup(self, gesture):
		self._launchByKey("diskcleanup")
	script_launchDiskCleanup.__doc__ = _("Disk Cleanup")
	script_launchDiskCleanup.category = "appOn"

	def script_launchEdge(self, gesture):
		self._launchByKey("edge")
	script_launchEdge.__doc__ = _("Microsoft Edge")
	script_launchEdge.category = "appOn"

	def script_launchEverything(self, gesture):
		self._launchByKey("everything")
	script_launchEverything.__doc__ = _("Everything")
	script_launchEverything.category = "appOn"

	def script_launchFirefox(self, gesture):
		self._launchByKey("firefox")
	script_launchFirefox.__doc__ = _("Mozilla Firefox")
	script_launchFirefox.category = "appOn"

	def script_launchGitHubDesktop(self, gesture):
		self._launchByKey("githubdesktop")
	script_launchGitHubDesktop.__doc__ = _("GitHub Desktop")
	script_launchGitHubDesktop.category = "appOn"

	def script_launchExcel(self, gesture):
		self._launchByKey("excel")
	script_launchExcel.__doc__ = _("Microsoft Excel")
	script_launchExcel.category = "appOn"

	def script_launchPowerPoint(self, gesture):
		self._launchByKey("powerpoint")
	script_launchPowerPoint.__doc__ = _("Microsoft PowerPoint")
	script_launchPowerPoint.category = "appOn"

	def script_launchMSWord(self, gesture):
		self._launchByKey("word")
	script_launchMSWord.__doc__ = _("Microsoft Word")
	script_launchMSWord.category = "appOn"

	def script_launchNotepad(self, gesture):
		self._launchByKey("notepad")
	script_launchNotepad.__doc__ = _("Notepad")
	script_launchNotepad.category = "appOn"

	def script_launchNotepadPlusPlus(self, gesture):
		self._launchByKey("notepadpp")
	script_launchNotepadPlusPlus.__doc__ = _("Notepad++")
	script_launchNotepadPlusPlus.category = "appOn"

	def script_launchPowershell(self, gesture):
		self._launchByKey("powershell", True)
	script_launchPowershell.__doc__ = _("PowerShell")
	script_launchPowershell.category = "appOn"

	def script_launchReaper(self, gesture):
		self._launchByKey("reaper")
	script_launchReaper.__doc__ = _("REAPER")
	script_launchReaper.category = "appOn"

	def script_launchRegedit(self, gesture):
		self._launchByKey("regedit", True)
	script_launchRegedit.__doc__ = _("Registry Editor")
	script_launchRegedit.category = "appOn"

	def script_launchThisPC(self, gesture):
		self._launchByKey("thispc")
	script_launchThisPC.__doc__ = _("This PC")
	script_launchThisPC.category = "appOn"

	def script_launchWinamp(self, gesture):
		self._launchByKey("winamp")
	script_launchWinamp.__doc__ = _("Winamp")
	script_launchWinamp.category = "appOn"

	def script_launchDefender(self, gesture):
		self._launchByKey("defender")
	script_launchDefender.__doc__ = _("Windows Security")
	script_launchDefender.category = "appOn"

	def script_launchWordPad(self, gesture):
		self._launchByKey("wordpad")
	script_launchWordPad.__doc__ = _("WordPad")
	script_launchWordPad.category = "appOn"

	def script_launchGoogleDrive(self, gesture):
		self._launchByKey("googledrive")
	script_launchGoogleDrive.__doc__ = _("Google Drive for Desktop")
	script_launchGoogleDrive.category = "appOn"

	def script_launchVSCode(self, gesture):
		self._launchByKey("vscode")
	script_launchVSCode.__doc__ = _("Visual Studio Code")
	script_launchVSCode.category = "appOn"

	def script_launchGit(self, gesture):
		self._launchByKey("git")
	script_launchGit.__doc__ = _("Git")
	script_launchGit.category = "appOn"

	def script_launchLibreOfficeCalc(self, gesture):
		self._launchByKey("libreofficecalc")
	script_launchLibreOfficeCalc.__doc__ = _("LibreOffice Calc")
	script_launchLibreOfficeCalc.category = "appOn"

	def script_launchLibreOfficeDraw(self, gesture):
		self._launchByKey("libreofficedraw")
	script_launchLibreOfficeDraw.__doc__ = _("LibreOffice Draw")
	script_launchLibreOfficeDraw.category = "appOn"

	def script_launchLibreOfficeImpress(self, gesture):
		self._launchByKey("libreofficeimpress")
	script_launchLibreOfficeImpress.__doc__ = _("LibreOffice Impress")
	script_launchLibreOfficeImpress.category = "appOn"

	def script_launchLibreOfficeMath(self, gesture):
		self._launchByKey("libreofficemath")
	script_launchLibreOfficeMath.__doc__ = _("LibreOffice Math")
	script_launchLibreOfficeMath.category = "appOn"

	def script_launchLibreOfficeWriter(self, gesture):
		self._launchByKey("libreofficewriter")
	script_launchLibreOfficeWriter.__doc__ = _("LibreOffice Writer")
	script_launchLibreOfficeWriter.category = "appOn"

	__gestures = {"kb:alt+windows+a": "showAppMenu"}
