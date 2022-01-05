#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2023 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import os
from enigma import getDesktop
from Tools.Directories import resolveFilename, SCOPE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS
from skin import loadSkin, loadSingleSkinData, dom_skins
from .Debug import logger
from .Version import ID, PLUGIN


def getSkinName(skin_name):
	return ID + skin_name


def getScalingFactor():
	return {"HD": 0.66, "FHD": 1, "WQHD": 1.33}[getResolution()]


def getResolution():
	height = getDesktop(0).size().height()
	resolution = "SD"
	if height > 576:
		resolution = "HD"
	if height > 720:
		resolution = "FHD"
	if height > 1080:
		resolution = "WQHD"
	return resolution


def getSkinPath(file_name):
	logger.debug("file_name: %s", file_name)
	resolution = getResolution()
	dirs = [
		(SCOPE_CURRENT_SKIN, os.path.join(PLUGIN, "skin")),
		(SCOPE_PLUGINS, os.path.join("Extensions", PLUGIN, "skin")),
		(SCOPE_SKIN, "")
	]
	logger.debug("dirs: %s", dirs)

	found = False
	for adir in dirs:
		for _resolution in [resolution, ""]:
			skin_path = os.path.join(resolveFilename(adir[0]), adir[1], _resolution, file_name)
			# logger.debug("checking: skin_path: %s", skin_path)
			if os.path.exists(skin_path):
				found = True
				break
		if found:
			break
	else:
		skin_path = None
	logger.debug("skin_path: %s", skin_path)
	return skin_path


def initPluginSkinPath():
	current_skin = os.path.join(resolveFilename(SCOPE_CURRENT_SKIN), PLUGIN)
	plugin_skin = os.path.join(resolveFilename(SCOPE_PLUGINS), "Extensions", PLUGIN)
	if not os.path.exists(plugin_skin):
		plugin_skin = os.path.join(resolveFilename(SCOPE_PLUGINS), "SystemPlugins", PLUGIN)
	logger.info("current_skin: %s", current_skin)
	logger.info("plugin_skin: %s", plugin_skin)
	if not os.path.isdir(current_skin):
		logger.info("%s > %s", current_skin, plugin_skin)
		os.symlink(plugin_skin, current_skin)


def loadPluginSkin(skin_file):
	loadSkin(getSkinPath(skin_file), "")
	path, dom_skin = dom_skins[-1:][0]
	loadSingleSkinData(getDesktop(0), dom_skin, path)
