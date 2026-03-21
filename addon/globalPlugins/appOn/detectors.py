# detectors.py
import os
import re
import addonHandler
import winreg
import ctypes

addonHandler.initTranslation()
try:
	_ = addonHandler.getTranslation()
except:
	def _(x): return x

def get_file_version(path):
	if not path or not os.path.exists(path): return ""
	try:
		size = ctypes.windll.version.GetFileVersionInfoSizeW(path, None)
		if not size: return ""
		res = ctypes.create_string_buffer(size)
		ctypes.windll.version.GetFileVersionInfoW(path, None, size, res)
		r = ctypes.c_void_p()
		l = ctypes.c_uint()
		if ctypes.windll.version.VerQueryValueW(res, "\\", ctypes.byref(r), ctypes.byref(l)):
			if l.value:
				class VS_FIXEDFILEINFO(ctypes.Structure):
					_fields_ = [("dwSignature", ctypes.c_uint32), ("dwStrucVersion", ctypes.c_uint32),
								("dwFileVersionMS", ctypes.c_uint32), ("dwFileVersionLS", ctypes.c_uint32),
								("dwProductVersionMS", ctypes.c_uint32), ("dwProductVersionLS", ctypes.c_uint32)]
				ffi = VS_FIXEDFILEINFO.from_address(r.value)
				return f"{ffi.dwFileVersionMS >> 16}.{ffi.dwFileVersionMS & 0xFFFF}.{ffi.dwFileVersionLS >> 16}.{ffi.dwFileVersionLS & 0xFFFF}"
	except: pass
	return ""

def getSpecialAppVersion(key, exePath):
	try:
		if key == "chrome" and exePath:
			parent = os.path.dirname(exePath)
			dirs = [d for d in os.listdir(parent) if re.match(r'^\d+\.', d)]
			if dirs: return sorted(dirs, key=lambda x: [int(i) for i in x.split('.')])[-1]
		if key == "firefox" and exePath:
			ini_path = os.path.join(os.path.dirname(exePath), "application.ini")
			if os.path.exists(ini_path):
				with open(ini_path, 'r') as f:
					content = f.read()
					match = re.search(r'^Version=(.+)$', content, re.M)
					if match: return match.group(1).strip()
	except: pass
	return ""

def getAppVersionFromRegistry(snippet):
	reg_paths = [
		(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
		(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
		(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Uninstall")
	]
	for hkey, base_path in reg_paths:
		try:
			with winreg.OpenKey(hkey, base_path) as root_key:
				for i in range(winreg.QueryInfoKey(root_key)[0]):
					try:
						sub_key_name = winreg.EnumKey(root_key, i)
						with winreg.OpenKey(root_key, sub_key_name) as sub_key:
							dname, _ = winreg.QueryValueEx(sub_key, "DisplayName")
							if snippet.lower() in dname.lower():
								ver, _ = winreg.QueryValueEx(sub_key, "DisplayVersion")
								return ver.strip()
					except: continue
		except: continue
	return ""

def findExe(paths):
	for p in paths:
		if not p: continue
		expanded = os.path.expandvars(p)
		if os.path.exists(expanded): return expanded
	return None

NO_VERSION_TOOLS_KEYS = {"diskcleanup", "thispc", "controlpanel", "cmd", "powershell", "regedit", "wordpad", "notepad", "defender"}

APP_REGISTRY_MAP = {
	"audacity": "Audacity", "brave": "Brave", "chrome": "Google Chrome",
	"edge": "Microsoft Edge", "everything": "Everything", "firefox": "Mozilla Firefox",
	"githubdesktop": "GitHub Desktop", "notepadpp": "Notepad++", "reaper": "REAPER", "winamp": "Winamp"
}

# List of paths aligned with original script by Chai
APP_DEFINITIONS = [
	("audacity", _("Audacity"), [r"C:\Program Files\Audacity\Audacity.exe", r"C:\Program Files (x86)\Audacity\Audacity.exe"]),
	("brave", _("Brave"), [r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe", r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"]),
	("chrome", _("Chrome"), [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"]),
	("edge", _("Edge"), [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe", r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"]),
	("everything", _("Everything"), [r"C:\Program Files\Everything\Everything.exe", r"C:\Program Files (x86)\Everything\Everything.exe", r"%LOCALAPPDATA%\Everything\Everything.exe"]),
	("firefox", _("Firefox"), [r"C:\Program Files\Mozilla Firefox\firefox.exe", r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"]),
	("githubdesktop", _("GitHub Desktop"), [r"%LOCALAPPDATA%\GitHubDesktop\GitHubDesktop.exe"]),  # <-- แก้ไข: เพิ่มวงเล็บเปิดและลบวงเล็บปิดส่วนเกิน
	("excel", _("Microsoft Excel"), [r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE", r"C:\Program Files\Microsoft Office\Office16\EXCEL.EXE", r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE"]),
	("powerpoint", _("Microsoft PowerPoint"), [r"C:\Program Files\Microsoft Office\root\Office16\POWERPNT.EXE", r"C:\Program Files\Microsoft Office\Office16\POWERPNT.EXE", r"C:\Program Files (x86)\Microsoft Office\root\Office16\POWERPNT.EXE"]),
	("word", _("Microsoft Word"), [r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE", r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE", r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE"]),
	("notepad", _("Notepad"), [r"C:\Windows\system32\notepad.exe", r"C:\Windows\notepad.exe"]),
	("notepadpp", _("Notepad++"), [r"C:\Program Files\Notepad++\notepad++.exe", r"C:\Program Files (x86)\Notepad++\notepad++.exe"]),
	("reaper", _("Reaper"), [r"C:\Program Files\REAPER (x64)\reaper.exe", r"C:\Program Files\REAPER\reaper.exe"]),
	("winamp", _("Winamp"), [r"C:\Program Files (x86)\Winamp\winamp.exe", r"C:\Program Files\Winamp\winamp.exe"]),
	("wordpad", _("WordPad"), [r"C:\Program Files\Windows NT\Accessories\wordpad.exe", r"C:\Program Files (x86)\Windows NT\Accessories\wordpad.exe"]),
	("diskcleanup", _("Disk Cleanup"), [r"%windir%\system32\cleanmgr.exe"]),
	("cmd", _("Command Prompt"), [r"cmd.exe"]),
	("controlpanel", _("Control Panel"), [r"control.exe"]),
	("powershell", _("PowerShell"), [r"powershell.exe"]),
	("regedit", _("Registry Editor"), [r"regedit.exe"]),
	("thispc", _("This PC"), [r"explorer.exe"]),
	("defender", _("Windows Defender"), [
		r"C:\Program Files\Windows Defender\MSASCui.exe",
		r"C:\Program Files (x86)\Windows Defender\MSASCui.exe"
	]),
	("googledrive", _("Google Drive for Desktop"), [r"C:\Program Files\Google\Drive File Stream\launch.bat", r"C:\Program Files\Google\Drive\launch.bat"]),
]