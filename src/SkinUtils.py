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


import os
from enigma import getDesktop
from Components.config import config
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from skin import loadSkin, loadSingleSkinData, dom_skins
from .Debug import logger
from .Version import ID, PLUGIN


def getSkinName(skin_name):
    return ID + skin_name


def getScalingFactor():
    return {"HD": 2.0 / 3.0, "FHD": 1, "WQHD": 4.0 / 3.0}[getResolution()]


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
    logger.debug(">>> file_name: %s", file_name)
    base_skin_dir = "/usr/share/enigma2"
    sub_skin_dir = os.path.dirname(config.skin.primary_skin.value)
    resolution = getResolution()
    logger.debug("resolution: %s, sub_skin_dir: %s", resolution, sub_skin_dir)
    if not sub_skin_dir:
        sub_skin_dir = "Default-HD"
    elif resolution == "FHD":
        if sub_skin_dir in ["Shadow-FHD", "Zombi-Shadow-FHD"]:
            sub_skin_dir = "Shadow-FHD"
        else:
            sub_skin_dir = "Default-FHD"
    elif resolution == "WQHD":
        if sub_skin_dir in ["Shadow-WQHD", "Default-WQHD"]:
            sub_skin_dir = "Default-WQHD"
        else:
            sub_skin_dir = "Other-WQHD"
    else:
        sub_skin_dir = "Default-HD"

    dirs = [
        os.path.join(resolveFilename(SCOPE_PLUGINS), "Extensions", PLUGIN, "skin", sub_skin_dir),
        os.path.join(resolveFilename(SCOPE_PLUGINS), "SystemPlugins", PLUGIN, "skin", sub_skin_dir),
        os.path.join(resolveFilename(SCOPE_PLUGINS), "Extensions", PLUGIN, "skin"),
        os.path.join(resolveFilename(SCOPE_PLUGINS), "SystemPlugins", PLUGIN, "skin"),
        os.path.join(base_skin_dir, sub_skin_dir),
        base_skin_dir
    ]
    logger.debug("dirs: %s", dirs)

    for adir in dirs:
        skin_path = os.path.join(adir, file_name)
        logger.debug("checking: skin_path: %s", skin_path)
        if os.path.exists(skin_path):
            break
        skin_path = ""
    logger.debug("skin_path: %s", skin_path)
    return skin_path


def loadPluginSkin(skin_file):
    logger.info("skin_path: %s", getSkinPath(skin_file))
    loadSkin(getSkinPath(skin_file), "")
    path, dom_skin = dom_skins[-1:][0]
    loadSingleSkinData(getDesktop(0), dom_skin, path)
