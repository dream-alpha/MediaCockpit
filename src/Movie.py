#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2019 by dream-alpha
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
from ServiceUtils import getService
from Screens.Screen import Screen
from Screens.MoviePlayer import MoviePlayer
from globals import FILE_PATH
from Components.Sources.MDCCurrentService import MDCCurrentService
from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.config import config


class MDCMoviePlayerSummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self.skinName = ["MDCMoviePlayerSummary"]
		self["Service"] = MDCCurrentService(session.nav, parent)


class MDCMoviePlayer(MoviePlayer, Screen):

	def __init__(self, session, file_list, file_index, slideshow_active=False):
		self.file_index = file_index
		self.file_list = file_list
		self.slideshow_active = slideshow_active
		self.current_file = self.file_list[self.file_index]
		playservice = getService(self.current_file[FILE_PATH])
		MoviePlayer.handleLeave = self.handleLeave
		MoviePlayer.playNext = self.NextService
		MoviePlayer.playPrev = self.PrevService
		Screen.__init__(self, session)
		MoviePlayer.__init__(self, session, playservice)
		self.skinName = ""
		if config.plugins.mediacockpit.show_movie_infobar.value:
			self.skinName = ["MDCMoviePlayer"]
		self.ENABLE_RESUME_SUPPORT = False
		self.ALLOW_SUSPEND = True
		self.skip = 5
		self["Service"] = MDCCurrentService(session.nav, self)
		self["end"] = Label(_("End"))
		self["actions"] = ActionMap(
			["MDCActions"],
			{
				"stop": self.handleLeave,
				"red": self.exit,
				"blue": self.toggleInfo,
				"exit": self.exit,
			},
			-1
		)

	def createSummary(self):
		return MDCMoviePlayerSummary

	def NextService(self):
		MoviePlayer.leavePlayer(self)

	def PrevService(self):
		MoviePlayer.leavePlayer(self)

	def handleLeave(self, ask=False, _error=False):
		print("MDC-I: Movie: handleLeave: ask: %s" % ask)
		self.is_closing = True
		self.close(self.slideshow_active)

	def exit(self):
		print("MDC-I: Movie: exit")
		self.is_closing = True
		self.close(False)

	def isPlaying(self):
		return self.seekstate == self.SEEK_STATE_PLAY

	def getCutList(self):
		# no cutlist support
		self.cut_list = []

	def getPosition(self):
		position = 0
		seek = self.getSeek()
		if seek is not None:
			pos = seek.getPlayPosition()
			#print("MDC: Movie: getPosition: getPlayPosition(): %s" % pos)
			if not pos[0]:
				position = pos[1]
		if self.skip:
			position = 0
		if self.skip > 0:
			self.skip -= 1
		#print("MDC: Movie: getPosition: position: %s" % position)
		return position

	def getLength(self):
		seek = self.getSeek()
		if seek is None:
			return 0
		else:
			length = seek.getLength()
			if length[0]:
				return 0
			return length[1]

	def toggleInfo(self):
		config.plugins.mediacockpit.show_movie_infobar.value = not config.plugins.mediacockpit.show_movie_infobar.value
