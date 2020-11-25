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


from Screens.Screen import Screen
from Components.Label import Label
from Components.Sources.StaticText import StaticText


class Display():

	def __init__(self):
		self["osd_info"] = Label()
		self["lcd_info"] = StaticText()
		self["lcd_title"] = StaticText()

	def displayLCD(self, title, info):
		#print("MDC: Display: displayLCD: title: %s, info: %s" % (title, info))
		self["lcd_title"].setText(title)
		self["lcd_info"].setText(info)

	def displayOSD(self, info):
		#print("MDC: Display: displayOSD: info: %s" % info)
		self["osd_info"].setText(info)

	def createSummary(self):
		return MDCDisplaySummary


class MDCDisplaySummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self.skinName = [self.__class__.__name__]
