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


from Components.Label import Label
from Components.Sources.StaticText import StaticText
from .__init__ import _


class Display():
    def __init__(self, csel):
        self.csel = csel
        self.csel["osd_info"] = Label()
        self.csel["lcd_info"] = StaticText()
        self.csel["lcd_title"] = StaticText()

    def displayLCD(self, title, info):
        # logger.debug("title: %s, info: %s", title, info)
        self.csel["lcd_title"].setText(title)
        self.csel["lcd_info"].setText(info)

    def displayOSD(self, info):
        # logger.debug("info: %s", info)
        self.csel["osd_info"].setText(_("MediaCockpit") + " - " + info)
