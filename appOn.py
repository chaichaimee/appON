# appOn.py
# -*- coding: utf-8 -*-
#
# Copyright (C) 2025 chai chaimee
# Licensed under GNU General Public License. See COPYING.txt for details.

import globalPluginHandler
import inputCore
import keyboardHandler
import subprocess
import psutil
import wx
import os
import winUser
import ctypes
from ctypes import wintypes
# Import ui module for speaking messages
import ui
import time

class GlobalPlugin(globalPluginHandler.GlobalPlugin):

    def __init__(self):
        super(GlobalPlugin, self).__init__()
        # Removed all gesture registrations as per user request
        self.registerGestures()
        # Initialize Win32 API for setting active window
        self.SetActiveWindow = winUser.user32.SetActiveWindow
        self.SetActiveWindow.argtypes = [wintypes.HWND]
        self.SetActiveWindow.restype = wintypes.BOOL

    def terminate(self):
        super(GlobalPlugin, self).terminate()

    def registerGestures(self):
        # All gestures are now unbound, users must add them manually.
        pass

    def isProcessRunning(self, process_name):
        """Check if a process is running."""
        for proc in psutil.process_iter(['name']):
            if proc.info['name'].lower() == process_name.lower():
                return True
        return False

    def findExe(self, possible_paths, exe_name):
        """Search for executable in common installation paths"""
        for path in possible_paths:
            expanded = os.path.expandvars(path)
            if os.path.exists(expanded):
                return expanded
        
        # Try to find via system PATH
        try:
            result = subprocess.run(['where', exe_name], 
                                  capture_output=True, text=True, shell=True)
            if result.returncode == 0:
                return result.stdout.splitlines()[0].strip()
        except:
            pass
        
        return None

    def _launchApp(self, exe_path, run_as_admin):
        """A centralized function to launch an application reliably."""
        try:
            if run_as_admin:
                # Use ShellExecuteW for reliable admin elevation
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", exe_path, None, None, 1
                )
            else:
                # Use subprocess.Popen for non-admin launches
                subprocess.Popen(exe_path, shell=False)
        except Exception as e:
            # Speak the error message
            ui.message(f"Error launching application: {str(e)}")

    def activateWindowByTitle(self, window_title):
        """Activate a window by its title using Win32 API"""
        try:
            hwnd = winUser.findWindow(0, window_title)
            if hwnd:
                # First, try to set the window to foreground
                winUser.setForegroundWindow(hwnd)
                # Then, try to set it as active window
                self.SetActiveWindow(hwnd)
                return True
        except:
            pass
        return False

    def activateOrLaunch(self, possible_paths, window_title, process_name, run_as_admin=False):
        """Activate a running application or launch it if not running."""
        try:
            # First try to activate the window by title
            if self.activateWindowByTitle(window_title):
                return
            
            # If not running, find path and launch
            exe_path = self.findExe(possible_paths, process_name)
            if not exe_path:
                ui.message(f"Could not find {process_name}")
                return
            
            # Launch the application
            self._launchApp(exe_path, run_as_admin)
            
            # Only wait and retry for specific, known-problematic applications
            if process_name.lower() in ["everything.exe", "msedge.exe"]:
                time.sleep(1)
                if self.activateWindowByTitle(window_title):
                    return
                ui.message(f"Waiting for {window_title}...")
                for _ in range(5):  # Retry up to 5 times
                    time.sleep(1)
                    if self.activateWindowByTitle(window_title):
                        ui.message(f"{window_title} is now active.")
                        return
                ui.message(f"Could not activate {window_title} after launch.")
        except Exception as e:
            ui.message(f"Error: {str(e)}")

    def launchSystemTool(self, command, window_title, run_as_admin=False):
        """Launch system tools with a reliable method."""
        try:
            # First try to activate the window by title
            if self.activateWindowByTitle(window_title):
                return
                
            if run_as_admin:
                # Use ShellExecuteW for reliable admin elevation
                ctypes.windll.shell32.ShellExecuteW(
                    None, "runas", command, None, None, 1
                )
            else:
                # Use subprocess.Popen for non-admin calls
                subprocess.Popen(command, shell=False)

            # Add a brief delay to allow the window to appear
            time.sleep(1)
            
            # Attempt to activate it again
            self.activateWindowByTitle(window_title)

        except Exception as e:
            ui.message(f"Error launching system tool: {str(e)}")

    def activateSettingsURI(self, uri, window_title, process_name):
        try:
            if self.activateWindowByTitle(window_title):
                return
                
            if self.isProcessRunning(process_name):
                # Wait a bit and try to activate again
                time.sleep(1)
                if self.activateWindowByTitle(window_title):
                    return
                    
            msascui_path = os.path.expandvars(r"%ProgramFiles%\Windows Defender\MSASCui.exe")
            if os.path.exists(msascui_path):
                subprocess.Popen(msascui_path, shell=False)
            else:
                subprocess.Popen(["start", "", uri], shell=True)
                
            # Wait for window to appear and try to activate it
            time.sleep(2)
            self.activateWindowByTitle(window_title)
        except Exception as e:
            ui.message(f"Error opening settings: {str(e)}")

    # All the script methods remain the same as before...
    def script_launchNotepadPlusPlus(self, gesture):
        paths = [
            r"C:\Program Files\Notepad++\notepad++.exe",
            r"C:\Program Files (x86)\Notepad++\notepad++.exe"
        ]
        self.activateOrLaunch(paths, "Notepad++", "notepad++.exe", run_as_admin=False)

    def script_launchNotepad(self, gesture):
        paths = [
            r"C:\Windows\system32\notepad.exe",
            r"C:\Windows\notepad.exe"
        ]
        self.activateOrLaunch(paths, "Notepad", "notepad.exe")

    def script_launchWordPad(self, gesture):
        paths = [
            r"C:\Program Files\Windows NT\Accessories\wordpad.exe",
            r"C:\Program Files (x86)\Windows NT\Accessories\wordpad.exe"
        ]
        self.activateOrLaunch(paths, "WordPad", "wordpad.exe")

    def script_launchMSWord(self, gesture):
        paths = [
            r"C:\Program Files\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files\Microsoft Office\Office16\WINWORD.EXE",
            r"C:\Program Files\Microsoft Office\Office15\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\Office16\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\Office15\WINWORD.EXE",
            r"C:\Program Files (x86)\Microsoft Office\Office14\WINWORD.EXE"
        ]
        self.activateOrLaunch(paths, "Microsoft Word", "WINWORD.EXE")

    def script_launchExcel(self, gesture):
        paths = [
            r"C:\Program Files\Microsoft Office\root\Office16\EXCEL.EXE",
            r"C:\Program Files\Microsoft Office\Office16\EXCEL.EXE",
            r"C:\Program Files\Microsoft Office\Office15\EXCEL.EXE",
            r"C:\Program Files (x86)\Microsoft Office\root\Office16\EXCEL.EXE",
            r"C:\Program Files (x86)\Microsoft Office\Office16\EXCEL.EXE",
            r"C:\Program Files (x86)\Microsoft Office\Office15\EXCEL.EXE",
            r"C:\Program Files (x86)\Microsoft Office\Office14\EXCEL.EXE"
        ]
        self.activateOrLaunch(paths, "Microsoft Excel", "EXCEL.EXE")

    def script_launchWinamp(self, gesture):
        paths = [
            r"C:\Program Files (x86)\Winamp\winamp.exe",
            r"C:\Program Files\Winamp\winamp.exe"
        ]
        self.activateOrLaunch(paths, "Winamp", "winamp.exe")

    def script_launchAudacity(self, gesture):
        paths = [
            r"C:\Program Files\Audacity\Audacity.exe",
            r"C:\Program Files (x86)\Audacity\Audacity.exe"
        ]
        self.activateOrLaunch(paths, "Audacity", "Audacity.exe")

    def script_launchEverything(self, gesture):
        paths = [
            r"C:\Program Files\Everything\Everything.exe",
            r"C:\Program Files (x86)\Everything\Everything.exe",
            r"%LOCALAPPDATA%\Everything\Everything.exe"
        ]
        self.activateOrLaunch(paths, "Everything", "Everything.exe")

    def script_launchChrome(self, gesture):
        paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        self.activateOrLaunch(paths, "Chrome", "chrome.exe")

    def script_launchReaper(self, gesture):
        paths = [
            r"C:\Program Files\REAPER (x64)\reaper.exe",
            r"C:\Program Files\REAPER\reaper.exe"
        ]
        self.activateOrLaunch(paths, "Reaper", "reaper.exe")

    def script_launchEdge(self, gesture):
        paths = [
            r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
        ]
        self.activateOrLaunch(paths, "Microsoft Edge", "msedge.exe")

    def script_launchGoogleDrive(self, gesture):
        paths = [
            r"C:\Program Files\Google\Drive File Stream\launch.bat",
            r"C:\Program Files\Google\Drive\launch.bat"
        ]
        self.activateOrLaunch(paths, "Google Drive for Desktop", "launch.bat")

    def script_launchFirefox(self, gesture):
        paths = [
            r"C:\Program Files\Mozilla Firefox\firefox.exe",
            r"C:\Program Files (x86)\Mozilla Firefox\firefox.exe"
        ]
        self.activateOrLaunch(paths, "Firefox", "firefox.exe")

    def script_launchDiskCleanup(self, gesture):
        paths = [r"%windir%\system32\cleanmgr.exe"]
        self.activateOrLaunch(paths, "Disk Cleanup", "cleanmgr.exe")

    def script_launchBrave(self, gesture):
        paths = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
        ]
        self.activateOrLaunch(paths, "Brave", "brave.exe")

    def script_launchDefender(self, gesture):
        msascui_path = os.path.expandvars(r"%ProgramFiles%\Windows Defender\MSASCui.exe")
        if os.path.exists(msascui_path):
            self.activateSettingsURI(msascui_path, "Windows Security", "MSASCui.exe")
        else:
            self.activateSettingsURI(r"windowsdefender://Threatsettings", "Windows Security", "SystemSettings.exe")

    def script_launchThisPC(self, gesture):
        """Open This PC (File Explorer)"""
        self.launchSystemTool("explorer.exe", "File Explorer")

    def script_launchControlPanel(self, gesture):
        """Open Control Panel"""
        self.launchSystemTool("control.exe", "Control Panel")

    def script_launchCmd(self, gesture):
        """Open Command Prompt"""
        self.launchSystemTool("cmd.exe", "Command Prompt", run_as_admin=True)

    def script_launchPowershell(self, gesture):
        """Open PowerShell"""
        self.launchSystemTool("powershell.exe", "Windows PowerShell", run_as_admin=True)

    # Script documentation
    script_launchNotepadPlusPlus.__doc__ = "Notepad++"
    script_launchNotepad.__doc__ = "Notepad"
    script_launchWordPad.__doc__ = "WordPad"
    script_launchMSWord.__doc__ = "Microsoft Word"
    script_launchExcel.__doc__ = "Microsoft Excel"
    script_launchWinamp.__doc__ = "Winamp"
    script_launchAudacity.__doc__ = "Audacity"
    script_launchEverything.__doc__ = "Everything"
    script_launchChrome.__doc__ = "Chrome"
    script_launchReaper.__doc__ = "Reaper"
    script_launchEdge.__doc__ = "Edge"
    script_launchGoogleDrive.__doc__ = "Google Drive for Desktop"
    script_launchFirefox.__doc__ = "Firefox"
    script_launchDiskCleanup.__doc__ = "Disk Cleanup"
    script_launchBrave.__doc__ = "Brave"
    script_launchDefender.__doc__ = "Windows Defender"
    script_launchThisPC.__doc__ = "This PC"
    script_launchControlPanel.__doc__ = "Control Panel"
    script_launchCmd.__doc__ = "Command Prompt"
    script_launchPowershell.__doc__ = "PowerShell"
    
    # Script categories
    script_launchNotepadPlusPlus.category = "appOn"
    script_launchNotepad.category = "appOn"
    script_launchWordPad.category = "appOn"
    script_launchMSWord.category = "appOn"
    script_launchExcel.category = "appOn"
    script_launchWinamp.category = "appOn"
    script_launchAudacity.category = "appOn"
    script_launchEverything.category = "appOn"
    script_launchChrome.category = "appOn"
    script_launchReaper.category = "appOn"
    script_launchEdge.category = "appOn"
    script_launchGoogleDrive.category = "appOn"
    script_launchFirefox.category = "appOn"
    script_launchDiskCleanup.category = "appOn"
    script_launchBrave.category = "appOn"
    script_launchDefender.category = "appOn"
    script_launchThisPC.category = "appOn"
    script_launchControlPanel.category = "appOn"
    script_launchCmd.category = "appOn"
    script_launchPowershell.category = "appOn"
