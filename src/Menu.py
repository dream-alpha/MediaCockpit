# !/usr/bin/python
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
from Screens.ChoiceBox import ChoiceBox
from .__init__ import _
from .Debug import logger
from .Version import PLUGIN
from .FileManagerUtils import FILE_OP_LOAD
from .FileManagerProgress import FileManagerProgress
from .ConfigScreen import ConfigScreen
from .About import about


class Menu():
    def __init__(self):
        logger.info("...")

    def openMenu(self):
        logger.info("...")
        alist = [
            ("%s" % _("Load cache directory"), "load_cache_dir"),
            ("%s" % _("Load cache bookmark"), "load_cache_bookmark"),
            ("%s" % _("Show load progress"), "show_load_progress"),
            ("%s" % _("Setup"), "open_setup"),
            ("%s" % _("About"), "about")
        ]

        self.session.openWithCallback(
            self.openMenuCallback,
            ChoiceBox,
            title=PLUGIN,
            list=alist,
            windowTitle=_("Menu"),
            allow_cancel=True,
            titlebartext=_("Input")
        )

    def openMenuCallback(self, answer=None):
        logger.info("...")
        if answer:
            screen = answer[1]
            if screen == "load_cache_dir":
                self.loadCacheDir()
            elif screen == "load_cache_bookmark":
                self.loadCacheBookmark()
            elif screen == "show_load_progress":
                self.session.open(FileManagerProgress, FILE_OP_LOAD)
            elif screen == "open_setup":
                self.openConfigScreen()
            elif screen == "open_setup":
                self.session.open(ConfigScreen, config.plugins.mediacockpit)
            elif screen == "about":
                about(self.session)
