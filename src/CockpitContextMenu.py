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


from Components.ActionMap import ActionMap
from Components.Sources.List import List
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Tools.BoundFunction import boundFunction
from .About import about
from .__init__ import _
from .SkinUtils import getSkinName


class CockpitContextMenu(Screen):

	def __init__(self, session, csel):
		Screen.__init__(self, session)
		self.skinName = getSkinName("CockpitContextMenu")
		self["title"] = StaticText()

		self["actions"] = ActionMap(
			["OkCancelActions", "ColorActions", "MenuActions"],
			{
				"cancel":	self.close,
				"ok":		self.ok,
				"red":		self.close,
				"menu":		csel.openConfigScreen,
			},
			-1
		)

		menu = []
		self.setTitle(_("Select function"))
		menu.append((_("Bookmarks"), (csel.openBookmarks, True)))
		menu.append((_("Setup"), (csel.openConfigScreen, True)))
		menu.append((_("About"), (boundFunction(about, session), True)))
		self["menu"] = List(menu)

	def ok(self):
		current_entry = self["menu"].getCurrent()
		current_entry[1][0]()
		if current_entry[1][1]:
			self.close()
