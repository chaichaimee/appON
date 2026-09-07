# settingsDialog.py

import wx
import gui
import addonHandler
from . import configStore

addonHandler.initTranslation()
try:
	_ = addonHandler.getTranslation()
except AttributeError:
	def _(x): return x

class AppOnSettingsDialog(wx.Dialog):
	def __init__(self, parent, appDefinitions):
		super().__init__(parent, title=_("AppOn Setting"))
		self.appDefinitions = appDefinitions
		disabledKeys = set(configStore.loadConfig().get("disabled_apps", []))

		panel = wx.Panel(self)
		outerSizer = wx.BoxSizer(wx.VERTICAL)

		listLabelText = _("Choose which apps appear in the AppOn menu:")
		instructionLabel = wx.StaticText(panel, label=listLabelText)
		outerSizer.Add(instructionLabel, 0, wx.ALL, 10)

		# wx.CheckListBox exposes its check state through list "selected" state
		# rather than a real checkbox state, so NVDA never announces
		# checked/not checked when toggling with Space. A scrollable panel of
		# individual wx.CheckBox controls is a genuine native checkbox per
		# item, which NVDA reads correctly and reliably.
		self.scrolledPanel = wx.ScrolledWindow(panel, style=wx.VSCROLL)
		self.scrolledPanel.SetScrollRate(0, 20)
		checkboxSizer = wx.BoxSizer(wx.VERTICAL)
		self.checkBoxes = []
		for key, displayName, paths in appDefinitions:
			checkbox = wx.CheckBox(self.scrolledPanel, label=displayName)
			checkbox.SetValue(key not in disabledKeys)
			checkboxSizer.Add(checkbox, 0, wx.ALL, 5)
			self.checkBoxes.append((key, checkbox))
		self.scrolledPanel.SetSizer(checkboxSizer)
		outerSizer.Add(self.scrolledPanel, 1, wx.EXPAND | wx.ALL, 10)

		# Buttons must be parented to the same window (panel) that manages the
		# sizer they sit in. CreateButtonSizer parents its buttons to the
		# Dialog itself, which mismatched the panel-based layout here and was
		# the root cause of OK/Cancel not responding to activation.
		okButton = wx.Button(panel, id=wx.ID_OK, label=_("OK"))
		cancelButton = wx.Button(panel, id=wx.ID_CANCEL, label=_("Cancel"))
		okButton.SetDefault()
		buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
		buttonSizer.Add(okButton, 0, wx.ALL, 5)
		buttonSizer.Add(cancelButton, 0, wx.ALL, 5)
		outerSizer.Add(buttonSizer, 0, wx.ALIGN_CENTER | wx.BOTTOM, 10)

		panel.SetSizer(outerSizer)
		panelSizer = wx.BoxSizer(wx.VERTICAL)
		panelSizer.Add(panel, 1, wx.EXPAND)
		self.SetSizerAndFit(panelSizer)
		self.SetSize((400, 500))
		self.scrolledPanel.FitInside()

		# wx.Dialog assigns its own initial focus once ShowModal begins,
		# which happens after __init__ runs and overrides a SetFocus() called
		# here directly. Deferring via wx.CallAfter, triggered from
		# EVT_INIT_DIALOG (fired at the true start of ShowModal), reliably
		# wins that race so the app list - not the OK button - is what a
		# blind user lands on first.
		self.Bind(wx.EVT_INIT_DIALOG, self._on_init_dialog)

	def _on_init_dialog(self, event):
		event.Skip()
		if self.checkBoxes:
			wx.CallAfter(self.checkBoxes[0][1].SetFocus)

	def getDisabledKeys(self):
		return [key for key, checkbox in self.checkBoxes if not checkbox.GetValue()]

def showSettingsDialog(appDefinitions, on_saved=None):
	dialog = AppOnSettingsDialog(gui.mainFrame, appDefinitions)
	gui.mainFrame.prePopup()
	try:
		result = dialog.ShowModal()
	finally:
		gui.mainFrame.postPopup()
	if result == wx.ID_OK:
		disabledKeys = dialog.getDisabledKeys()
		configData = configStore.loadConfig()
		configData["disabled_apps"] = disabledKeys
		configStore.saveConfig(configData)
		if on_saved:
			on_saved()
	dialog.Destroy()
