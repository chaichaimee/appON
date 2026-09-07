![NVDA Logo](https://www.nvaccess.org/files/nvda/documentation/userGuide/images/nvda.ico)

# appOn

Your applications, one hotkey away. appOn is a fast, accessible launcher menu that detects the programs already installed on your PC and opens any of them instantly, without hunting through the Start Menu or the desktop.

**author:** chai chaimee

**url:** https://github.com/chaichaimee/appOn

## Introduction

appOn adds a single, unified "app launcher" menu to NVDA. Press one hotkey and a list pops up showing every supported application that appOn has found installed on your computer — web browsers, office programs, text editors, multimedia tools, system utilities, and developer tools. Simply arrow down to the one you want and press Enter, and it launches immediately.

Behind the scenes, appOn quietly scans your system in the background (checking common install locations and the Windows Registry) so the menu is ready the moment you need it, and it keeps a small settings screen where you can choose exactly which applications should appear in your personal menu.

### Hot Keys

> **Alt+Windows+A**
> Single Tap : Open the appOn application launcher menu

> Every individual "launch this specific app" command (for example, launching Chrome or opening the Registry Editor directly) is included as its own NVDA script but has **no default hotkey**. If you want a direct shortcut to a particular application, assign one yourself from NVDA's Input Gestures dialog, under the "appOn" category.

## Features

### 1. The AppOn Menu

Pressing **Alt+Windows+A** opens a floating "AppOnMenu" window containing a single list of every detected, enabled application.

Step-by-step behavior:

1. Use the Up and Down arrow keys to move through the list of applications.
2. Press Enter (or double-click) to launch the highlighted application; the menu closes automatically.
3. Press Escape at any time to close the menu without launching anything.
4. If you press the hotkey again while the menu is already open, appOn does not open a second copy — it simply brings the existing menu window back to the foreground and gives it focus.

To make list browsing cleaner for screen reader users, appOn removes the usual "item X of Y" position announcement from the entries in this specific menu, so NVDA reads only the application name.

### 2. Automatic Application Detection and Caching

appOn does not ask you to configure file paths manually. As soon as NVDA loads the add-on, a background thread scans a built-in list of well-known applications and checks whether each one is actually installed, by testing a set of typical install locations (for example, both the 64-bit and 32-bit Program Files folders).

Only applications that are actually found on your system (or that are always-available Windows tools) are added to the menu. This scan runs once in the background so it never slows down or blocks NVDA, and the menu automatically refreshes itself with the results as soon as the scan finishes.

### 3. Version Detection

Where possible, appOn shows the installed version number next to the application name in the menu (for example, "Google Chrome 128.0.6613.120"). It works out the version using several methods, tried in order:

1. For Google Chrome, it looks inside the Chrome install folder for the versioned sub-folder and uses the highest version number found there.
2. For Mozilla Firefox, it reads the version directly out of Firefox's own "application.ini" file.
3. For most other applications, it looks up the application's "DisplayVersion" in the Windows Registry uninstall keys.
4. As a final fallback, it reads the version number embedded directly in the application's .exe file.
5. Microsoft Word, Excel, and PowerPoint are always labeled simply as "2024" rather than a detailed build number.
6. Plain system tools such as Command Prompt, Control Panel, Disk Cleanup, PowerShell, Registry Editor, This PC, Windows Security, Notepad, and WordPad never show a version number, since they are core parts of Windows itself.

### 4. Categories and Sorting

Every detected application is automatically placed into one of the following categories: Browsers, Documents, Text Editors, Multimedia, System Tools, Utilities, Development Tools, or Others (for anything uncategorized).

While the appOn menu is open, right-click inside the list (or open the context menu) to choose how the list is ordered:

1. **Sort A-Z** — every application listed together in a single, plain alphabetical order.
2. **Sort by Category** — applications are grouped under their category first, then alphabetized within each group.

Whichever sorting mode you pick is remembered and automatically used again the next time you open the menu.

### 5. AppOn Settings (Choosing Which Apps Appear)

The last item in the appOn menu is always "AppOn Setting". Selecting it closes the menu and opens a settings dialog listing every application appOn knows about, each with its own checkbox.

Step-by-step behavior:

1. When the dialog opens, focus is placed directly on the first checkbox in the list, ready for you to start reviewing right away.
2. Uncheck any application you never want to see in your appOn menu; leave it checked to keep it available.
3. Choose OK to save your choices, or Cancel to discard them.
4. Any application you unchecked is immediately hidden from the appOn menu, without needing to restart NVDA.

Real, individually-focusable checkboxes are used for this list rather than a single checkable listbox, specifically so NVDA correctly announces "checked" or "not checked" as you move through the options.

### 6. Launching Applications

When you choose an application, appOn starts it directly. A few applications are launched with special handling:

1. **Command Prompt, PowerShell, and Registry Editor** are launched with administrator privileges, so Windows will show the usual "Do you want to allow this app…" elevation prompt.
2. **Windows Security** first tries to launch its main program file directly; if that file cannot be found on your system, appOn instead opens the Windows Security app using its built-in "windowsdefender:" link.
3. All other applications are started using their normal program file, with any Windows environment variables (such as %LOCALAPPDATA%) automatically expanded.
4. If an application cannot be started for any reason, NVDA speaks an error message describing the problem instead of failing silently.

### 7. Live List Refresh

If the appOn menu is left open while the background application scan is still finishing up, the list of applications shown will automatically refresh itself in place as soon as the scan completes — you do not need to close and reopen the menu to see newly-detected applications.

### 8. Reliable Window Focus

Windows normally prevents background programs from stealing keyboard focus from whatever window you are currently using. To make sure the appOn menu reliably comes to the front and receives focus every time you open it, appOn uses a documented Windows technique that temporarily links its input thread with your current window's input thread just long enough to bring itself to the foreground.

### 9. Settings Storage and Migration

Your sort-order choice and your enabled/disabled application list are saved to a small configuration file stored inside your NVDA user configuration folder, under "ChaiChaimee\appOn\appOn.json". If appOn detects settings saved by an older version of the add-on in a previous file location, it automatically copies them over into the new location the first time it runs, so your preferences are never lost during an update.

### 10. Supported Applications

appOn can detect and launch the following applications, organized by category:

**Browsers:** Google Chrome, Microsoft Edge, Mozilla Firefox, Brave

**Documents:** Microsoft Word, Microsoft Excel, Microsoft PowerPoint, LibreOffice Writer, LibreOffice Calc, LibreOffice Impress, LibreOffice Draw, LibreOffice Math

**Text Editors:** Notepad, Notepad++, WordPad

**Multimedia:** Audacity, Winamp, REAPER

**System Tools:** Command Prompt, PowerShell, Control Panel, Disk Cleanup, Registry Editor, This PC, Windows Security

**Utilities:** Everything, GitHub Desktop, Google Drive for Desktop

**Development Tools:** Visual Studio Code, Git


## Support Me

If this tool has made your life easier, consider fueling the next update with a small donation.

[![Support me](https://img.shields.io/badge/Donate-Support%20Me-blue?style=for-the-badge&logo=stripe)](https://buy.stripe.com/dRm9AU1xQ3Ds22N6VK1VK01)

Your support means the world. Let's build something great together

© 2026 Chai Chaimee NVDA Add-on Released under GNU GPL