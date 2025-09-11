#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
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


from Components.config import config
from Plugins.Plugin import PluginDescriptor
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from .__init__ import _
from .Debug import logger
from .SkinUtils import loadPluginSkin
from .Version import ID, VERSION
from .MediaCockpit import MediaCockpit
from .ConfigInit import ConfigInit


def openMediaCockpit(session, **__):
    logger.info("...")
    session.open(MediaCockpit)


def autoStart(reason, **kwargs):
    if reason == 0:  # startup
        if "session" in kwargs:
            logger.info("+++ Version: %s starts...", VERSION)
            # session = kwargs["session"]
            MountCockpit.getInstance().registerBookmarks(
                ID, config.plugins.mediacockpit.bookmarks.value)
            loadPluginSkin("skin.xml")
    elif reason == 1:  # shutdown
        logger.info("--- shutdown")


def Plugins(**__):
    ConfigInit()
    descriptors = [
        PluginDescriptor(
            name="MediaCockpit",
            description=_("Pictures, Movies, and Slideshows"),
            where=[
                PluginDescriptor.WHERE_PLUGINMENU,
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
