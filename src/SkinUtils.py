#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2019 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	For more information on the GNU General Public License see:
#	<http://www.gnu.org/licenses/>.


import os
from Version import PLUGIN
from enigma import getDesktop
from skin import loadSkin, loadSingleSkinData, dom_skins
from Tools.Directories import fileExists, resolveFilename, SCOPE_SKIN, SCOPE_CURRENT_SKIN, SCOPE_PLUGINS


def getSkinPath(filename):
	#print("MDC: SkinUtils: getSkinPath: filename: %s" % filename)
	skin_path = resolveFilename(SCOPE_CURRENT_SKIN, PLUGIN + "/skin/" + filename)
	if not fileExists(skin_path):
		skin_path = resolveFilename(SCOPE_SKIN, "Default-FHD/" + PLUGIN + "/skin/" + filename)
	#print("MDC: SkinUtils: getSkinPath: skin_path: %s" % skin_path)
	return skin_path


def initSkinPath():
	default_skin = resolveFilename(SCOPE_SKIN, "Default-FHD/" + PLUGIN)
	current_skin = resolveFilename(SCOPE_CURRENT_SKIN, PLUGIN)
	plugin_skin = resolveFilename(SCOPE_PLUGINS, "Extensions/" + PLUGIN)
	print("MDC-I: SkinUtils: loadPluginSkin: current_skin: %s" % current_skin)
	print("MDC-I: SkinUtils: loadPluginSkin: default_skin: %s" % default_skin)
	print("MDC-I: SkinUtils: loadPluginSkin: plugin_skin: %s" % plugin_skin)
	if not os.path.isdir(default_skin):
		print("MDC-I: SkinUtils: loadPluginSkin: ln -s " + plugin_skin + " " + resolveFilename(SCOPE_SKIN, "Default-FHD"))
		os.system("ln -s " + plugin_skin + " " + resolveFilename(SCOPE_SKIN, "Default-FHD"))


def loadPluginSkin(skin_file):
	loadSkin(getSkinPath(skin_file), "")
	path, dom_skin = dom_skins[-1:][0]
	loadSingleSkinData(getDesktop(0), dom_skin, path)
