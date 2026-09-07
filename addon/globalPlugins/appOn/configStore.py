# configStore.py

import globalVars
import json
import os
import logHandler

LEGACY_CONFIG_PATH = os.path.join(globalVars.appArgs.configPath, "ChaiChaimee", "appOn.json")
CONFIG_PATH = os.path.join(globalVars.appArgs.configPath, "ChaiChaimee", "appOn", "appOn.json")

_DEFAULT_CONFIG = {"sort_mode": "alphabet", "disabled_apps": []}

def _migrateLegacyConfig():
	if os.path.exists(CONFIG_PATH):
		return
	if not os.path.exists(LEGACY_CONFIG_PATH):
		return
	try:
		with open(LEGACY_CONFIG_PATH, 'r', encoding='utf-8') as legacyFile:
			legacyData = json.load(legacyFile)
	except Exception as err:
		logHandler.log.error(f"AppOn legacy config read failed during migration: {err}")
		return
	try:
		os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
		with open(CONFIG_PATH, 'w', encoding='utf-8') as newFile:
			json.dump(legacyData, newFile)
		logHandler.log.info("AppOn config migrated from ChaiChaimee\\appOn.json to ChaiChaimee\\appOn\\appOn.json")
	except Exception as err:
		logHandler.log.error(f"AppOn config write failed during migration: {err}")

def loadConfig():
	_migrateLegacyConfig()
	if not os.path.exists(CONFIG_PATH):
		return dict(_DEFAULT_CONFIG)
	try:
		with open(CONFIG_PATH, 'r', encoding='utf-8') as configFile:
			storedData = json.load(configFile)
	except Exception as err:
		logHandler.log.error(f"AppOn config read failed: {err}")
		return dict(_DEFAULT_CONFIG)
	mergedData = dict(_DEFAULT_CONFIG)
	mergedData.update(storedData)
	return mergedData

def saveConfig(data):
	try:
		os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
		with open(CONFIG_PATH, 'w', encoding='utf-8') as configFile:
			json.dump(data, configFile)
	except Exception as err:
		logHandler.log.error(f"AppOn config write failed: {err}")
