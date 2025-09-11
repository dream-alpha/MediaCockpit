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


instance = None


class MerlinMusicPlayerWidget():

    def __init__(self):
        config.plugins.mediacockpit.non_standard_decoder.value = False

    def execBegin(self):
        return

    def execEnd(self):
        return

    def destroy(self):
        return

    def setCover(self, _cover):
        return


class eMerlinMusicPlayer():

    def __init__(self):
        return

    @staticmethod
    def getInstance():
        global instance
        if instance is None:
            instance = eMerlinMusicPlayer()
        return instance

    def setFunc(self, _func):
        return

    def enableAlsa(self, _enable):
        return

    def enableGapless(self, _enable):
        return
