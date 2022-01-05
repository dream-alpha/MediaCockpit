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
from Plugins.Plugin import PluginDescriptor
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from Components.config import config
from .__init__ import _
from .Debug import logger, createLogFile
from .SkinUtils import initPluginSkinPath, loadPluginSkin
from .Version import ID, VERSION
from .MediaCockpit import MediaCockpit
from .ConfigInit import ConfigInit
from .FileUtils import deleteFile, touchFile


def openMediaCockpit(session, **__):
	logger.info("...")
	session.open(MediaCockpit)


def autoStart(reason, **kwargs):
	if reason == 0:  # startup
		if "session" in kwargs:
			logger.info("+++ Version: %s starts...", VERSION)
			# session = kwargs["session"]
			touchFile("/etc/enigma2/.mdc")
			MountCockpit.getInstance().registerBookmarks(ID, config.plugins.mediacockpit.bookmarks.value)
			initPluginSkinPath()
			loadPluginSkin("skin.xml")
	elif reason == 1:  # shutdown
		logger.info("--- shutdown")
		deleteFile("/etc/enigma2/.mdc")
	else:
		logger.info("reason not handled: %s", reason)


def Plugins(**__):
	logger.info("+++ Plugins")
	ConfigInit()
	if os.path.exists("/etc/enigma2/.mdc"):
		createLogFile()
	descriptors = [
		PluginDescriptor(
			name="MediaCockpit",
			description=_("Pictures, Movies, and Slideshows"),
			where=[
				PluginDescriptor.WHERE_PLUGINMENU,
				PluginDescriptor.WHERE_EXTENSIONSMENU,
			],
			fnc=openMediaCockpit,
			icon="MediaCockpit.svg"
		),
		PluginDescriptor(
			where=[
				PluginDescriptor.WHERE_SESSIONSTART,
				PluginDescriptor.WHERE_AUTOSTART
			],
			fnc=autoStart,
		),
	]
	return descriptors
