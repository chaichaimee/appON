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
import controlTypes

addonHandler.initTranslation()
try:
	_ = addonHandler.getTranslation()
except:
	def _(x): return x

class NoPositionListItem(NVDAObject):
	def _get_positionInfo(self): return {}

class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = "appOn"
	CONFIG_PATH = os.path.join(globalVars.appArgs.configPath, "ChaiChaimee", "appOn.json")

	def chooseNVDAObjectOverlayClasses(self, obj, clsList):
		if obj.role == controlTypes.ROLE_LISTITEM:
			p = obj.parent
			while p:
				if p.role == controlTypes.ROLE_WINDOW and p.name == _("AppOnMenu"):
					clsList.insert(0, NoPositionListItem)
					break
				p = p.parent

	def _get_category(self, key):
		cats = {
			"1_Browsers": ["chrome", "edge", "firefox", "brave"],
			"2_Documents": ["word", "excel", "powerpoint"],
			"3_Text Editors": ["notepad", "notepadpp", "wordpad"],
			"4_Multimedia": ["audacity", "winamp", "reaper"],
			"5_System Tools": ["cmd", "powershell", "controlpanel", "diskcleanup", "regedit", "thispc", "defender"],
			"6_Utilities": ["everything", "githubdesktop", "googledrive"]
		}
		for cat, keys in cats.items():
			if key in keys: return cat
		return "7_Others"

	def _getAvailableAppItems(self, sort_mode="alphabet"):
		items = []
		app_map = {
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
		
		for key, display_name, paths in detectors.APP_DEFINITIONS:
			exePath = detectors.findExe(paths)
			if exePath or key in detectors.NO_VERSION_TOOLS_KEYS:
				version = ""
				if key not in detectors.NO_VERSION_TOOLS_KEYS:
					if key in ("word", "excel", "powerpoint"): version = " 2024"
					else:
						ver = detectors.getSpecialAppVersion(key, exePath) or \
							  detectors.getAppVersionFromRegistry(detectors.APP_REGISTRY_MAP.get(key, "")) or \
							  (detectors.get_file_version(exePath) if exePath else "")
						if ver: version = f" {ver}"
				
				label = f"{display_name}{version}"
				cat = self._get_category(key)
				method = app_map.get(key)
				if method:
					items.append({"label": label, "method": method, "cat": cat, "key": key})

		if sort_mode == "category":
			items.sort(key=lambda x: (x["cat"], x["label"].lower()))
		else:
			items.sort(key=lambda x: x["label"].lower())
			
		return [(i["label"], i["method"]) for i in items]

	def _launchByKey(self, key, admin=False):
		# Special handling for Windows Defender
		if key == "defender":
			paths = next((p for k, n, p in detectors.APP_DEFINITIONS if k == key), [])
			exePath = detectors.findExe(paths)
			if exePath:
				try:
					os.startfile(exePath)
				except Exception as e:
					ui.message(_("Error: {error}").format(error=str(e)))
			else:
				# Fallback to Windows Security URI
				try:
					import ctypes
					ctypes.windll.shell32.ShellExecuteW(None, "open", "windowsdefender://Threatsettings", None, None, 1)
				except Exception as e:
					ui.message(_("Error opening Windows Security: {error}").format(error=str(e)))
			return

		# Original logic for other apps
		paths = next((p for k, n, p in detectors.APP_DEFINITIONS if k == key), [])
		exePath = detectors.findExe(paths)
		if not exePath:
			exePath = paths[0] if paths else key
			
		try:
			if admin:
				import ctypes
				ctypes.windll.shell32.ShellExecuteW(None, "runas", exePath, None, None, 1)
			else:
				os.startfile(os.path.expandvars(exePath))
		except Exception as e:
			ui.message(_("Error: {error}").format(error=str(e)))

	def script_showAppMenu(self, gesture):
		wx.CallAfter(menu.showAppMenu, self._getAvailableAppItems, lambda cb: cb(None), self.CONFIG_PATH)
	script_showAppMenu.category = "appOn"
	script_showAppMenu.__doc__ = _("Shows the appOn menu.")

	# --- Tuned script launchers to use path checking system ---
	def script_launchAudacity(self, g): self._launchByKey("audacity")
	def script_launchBrave(self, g): self._launchByKey("brave")
	def script_launchChrome(self, g): self._launchByKey("chrome")
	def script_launchCmd(self, g): self._launchByKey("cmd", True)
	def script_launchControlPanel(self, g): self._launchByKey("controlpanel")
	def script_launchDiskCleanup(self, g): self._launchByKey("diskcleanup")
	def script_launchEdge(self, g): self._launchByKey("edge")
	def script_launchEverything(self, g): self._launchByKey("everything")
	def script_launchFirefox(self, g): self._launchByKey("firefox")
	def script_launchGitHubDesktop(self, g): self._launchByKey("githubdesktop")
	def script_launchExcel(self, g): self._launchByKey("excel")
	def script_launchPowerPoint(self, g): self._launchByKey("powerpoint")
	def script_launchMSWord(self, g): self._launchByKey("word")
	def script_launchNotepad(self, g): self._launchByKey("notepad")
	def script_launchNotepadPlusPlus(self, g): self._launchByKey("notepadpp")
	def script_launchPowershell(self, g): self._launchByKey("powershell", True)
	def script_launchReaper(self, g): self._launchByKey("reaper")
	def script_launchRegedit(self, g): self._launchByKey("regedit", True)
	def script_launchThisPC(self, g): self._launchByKey("thispc")
	def script_launchWinamp(self, g): self._launchByKey("winamp")
	def script_launchDefender(self, g): self._launchByKey("defender")
	def script_launchWordPad(self, g): self._launchByKey("wordpad")
	def script_launchGoogleDrive(self, g): self._launchByKey("googledrive")

	# Auto-set category
	for name in list(locals().keys()):
		if name.startswith("script_launch"):
			item = locals()[name]
			if callable(item):
				item.category = "appOn"

	__gestures = {"kb:alt+windows+a": "showAppMenu"}