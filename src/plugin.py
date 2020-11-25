#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2020 by dream-alpha
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


from __init__ import _
from Plugins.Plugin import PluginDescriptor
from Screens.InfoBar import InfoBar
from Components.config import config
from SkinUtils import initPluginSkinPath, loadPluginSkin
from Tools.BoundFunction import boundFunction
from Version import VERSION
from Cockpit import Cockpit
from ConfigInit import ConfigInit


def autoStart(reason, **kwargs):
	print("MDC-I: plugin: autoStart: reason: %s" % reason)
	if reason == 0:  # startup
		if "session" in kwargs:
			print("MDC-I: plugin: autoStart: +++ Version: " + VERSION + " starts...")
			session = kwargs["session"]
			launch_key = config.plugins.mediacockpit.launch_key.value
			if launch_key == "showMovies":
				InfoBar.showMovies = boundFunction(startMediaCockpit, session)
			elif launch_key == "showTv":
				InfoBar.showTv = boundFunction(startMediaCockpit, session)
			elif launch_key == "showRadio":
				InfoBar.showRadio = boundFunction(startMediaCockpit, session)
			elif launch_key == "openQuickbutton":
				InfoBar.openQuickbutton = boundFunction(startMediaCockpit, session)
			elif launch_key == "startTimeshift":
				InfoBar.startTimeshift = boundFunction(startMediaCockpit, session)
	elif reason == 1:  # shutdown
		print("MDC-I: plugin: autoStart: --- shutdown")
	else:
		print("MDC-I: plugin: autoStart: reason not handled: %s" % reason)


def startMediaCockpit(session, **__):
	initPluginSkinPath()
	loadPluginSkin("skin.xml")
	session.open(Cockpit)


def Plugins(**__):
	ConfigInit()
	return [
		PluginDescriptor(
			name=_("MediaCockpit"),
			description=_("Pictures, Movies, and Slideshows"),
			where=PluginDescriptor.WHERE_PLUGINMENU,
			fnc=startMediaCockpit,
			icon="mediacockpit.svg"
		),
		PluginDescriptor(
			where=[
				PluginDescriptor.WHERE_SESSIONSTART,
				PluginDescriptor.WHERE_AUTOSTART
			],
			fnc=autoStart,
		),
	]
