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


from Screens.InfoBarGenerics import InfoBarCueSheetSupport
from .Debug import logger
from .CutList import CutList
from .CutListUtils import removeFirstMarks


class CockpitCueSheet(InfoBarCueSheetSupport, CutList):

    def __init__(self, service):
        self.service = service
        InfoBarCueSheetSupport.__init__(self)
        CutList.__init__(self)
        self.cut_list = []

    def getCutList(self):
        logger.info("cut_list: %s", self.cut_list)
        return self.cut_list

    def downloadCuesheet(self):
        path = self.service.getPath() if self.service else None
        self.cut_list = self.readCutList(path)
        self.cut_list = removeFirstMarks(self.cut_list)
        logger.debug("path: %s, cut_list: %s", path, self.cut_list)

    def uploadCuesheet(self):
        path = self.service.getPath() if self.service else None
        logger.debug("path: %s, cut_list: %s", path, self.cut_list)
        self.writeCutList(self.service.getPath(), self.cut_list)
