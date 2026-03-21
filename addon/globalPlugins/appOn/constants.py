# constants.py
# Copyright (C) 2026 Chai Chaimee
# Licensed under GNU General Public License. See COPYING.txt for details.

import addonHandler

addonHandler.initTranslation()
try:
    _ = addonHandler.getTranslation()
except AttributeError:
    def _(x):
        return x

# List of all applications (name, paths, process_name, launch_method)
# Used in _getAvailableAppItems to build menu
APP_DEFINITIONS = [
    # (display name, check function, launch function)
    # Check functions are created in detectors.py using makeActivateCheck, makeSystemCheck, etc.
]

# List of system tools that do not need version display
NO_VERSION_TOOLS = {
    "Disk Cleanup", "This PC", "Control Panel",
    "Command Prompt", "PowerShell", "Registry Editor",
    "WordPad", "Notepad", "Windows Defender"
}