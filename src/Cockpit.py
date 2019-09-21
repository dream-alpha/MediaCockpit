#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2019 by dream-alpha
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


import os
from __init__ import _
from Movie import MDCMoviePlayer
from ConfigScreen import ConfigScreen
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.config import config
from enigma import getDesktop
from Picture import MDCPicturePlayer
from globals import FILE_TYPE, FILE_PATH, FILE_MEDIA, TYPE_DIR, TYPE_FILE, TYPE_M3U, TYPE_GOUP
from FileList import FileList
from MediaInfo import MediaInfo
from DelayTimer import DelayTimer
from Tiles import Tiles
from FileOps import FileOps
from ConfigInit import sort_modes
from Display import Display


def stopService(session, lastservice):
	#print("MDC: Cockpit: stopService: clear video buffer")
	session.nav.stopService()
	session.nav.playService(lastservice)
	session.nav.stopService()


def startService(session, lastservice):
	#print("MDC: Cockpit: startService: start")
	session.nav.playService(lastservice)


class Cockpit(Display, Tiles, FileOps, FileList, HelpableScreen, Screen):

	def __init__(self, session):
		print("MDC-I: Cockpit: __init__: session: %s" % session)
		FileList.__init__(self)

		self.file_list = []
		self.file_index = -1
		self.lastservice = None
		self.slideshow_file_index = -1
		self.thumbnail_size = None
		self.sort_modes = sort_modes
		self.load_path = None
		self.busy = False

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		Display.__init__(self)

		self["actions"] = HelpableActionMap(
			self,
			"MDCActions",
			{
				"playpause":	(self.playpause,	_("Pause/Resume") + " " + _("Slideshow")),
				"nextBouquet":	(self.prevPage,		_("Previous page")),
				"prevBouquet":	(self.nextPage,		_("Next page")),
				"right":	(self.moveRight,	_("Next picture")),
				"left":		(self.moveLeft,		_("Previous picture")),
				"up":		(self.moveUp,		_("Previous line")),
				"down":		(self.moveDown,		_("Next line")),
				"ok":		(self.processOk,	_("Ok")),
				"info":		(self.openInfo,		_("Information")),
				"menu":		(self.openMenu, 	_("Settings")),
				"red":		(self.red,		_("Delete file")),
				"green":	(self.green,		_("Ok")),
				"exit":		(self.exit,		_("Exit")),
				"0":		(self.moveHome,		_("Home")),
				"keyPrev":	(self.prevDirectory,	_("Previous directory")),
			},
			prio=-1
		)

		self["no_support"] = Label(_("Skin resolution other than Full HD is not supported yet"))

		Tiles.__init__(self)
		FileOps.__init__(self, session)
		self.desktop_size = getDesktop(0).size()
		self.skinName = self.getSkinName()

		if config.plugins.mediacockpit.start_home_dir.value:
			self.last_path = config.plugins.mediacockpit.home_dir.value
		else:
			self.last_path = config.plugins.mediacockpit.last_path.value
		print("MDC-I: Cockpit: __init__: last_path: %s" % self.last_path)

		self.first_start = True
		self.current_path = None
		self.dir_stack = []

		animations_enabled = getDesktop(0).isAnimationsEnabled()
		print("MDC-I: Cockpit: __init__: animations_enabled: %s" % animations_enabled)
		self.onLayoutFinish.append(self.LayoutFinish)

	def getSkinName(self):
		skin_name = "MDCCockpit"
		if self.desktop_size.width() != 1920:
			skin_name = "MDCNoSupport"
			self.setTitle(_("Information"))
		return skin_name

	def LayoutFinish(self):
		print("MDC-I: Cockpit: LayoutFinish")
		if self.first_start:
			self.first_start = False
			self.initTileAttribs()
			DelayTimer(10, self.firstStart, True)
			#print("MDC: Cockpit: LayoutFinish: thumbnail_size: (%s, %s)" % (self.thumbnail_size.width(), self.thumbnail_size.height()))

	def firstStart(self, first_start):
		print("MDC-I: Cockpit: firstStart: first_start: %s" % first_start)
		self.file_list_sort = config.plugins.mediacockpit.sort.value
		self.recurse_dirs = config.plugins.mediacockpit.recurse_dirs.value
		#print("MDC: Cockpit: firstStart: recurse_dirs: %s" % self.recurse_dirs)
		self.sort_across_dirs = config.plugins.mediacockpit.sort_across_dirs.value
		self.show_goup_tile = config.plugins.mediacockpit.show_goup_tile.value
		self.create_thumbnails = config.plugins.mediacockpit.create_thumbnails.value
		self.show_loading_details = config.plugins.mediacockpit.show_loading_details.value

		if not first_start:
			self.initTileAttribs()

		if first_start:
			self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()
		if not config.plugins.mediacockpit.tv_background.value:
			stopService(self.session, self.lastservice)
		else:
			startService(self.session, self.lastservice)

		last_path = self.last_path
		if not os.path.isdir(self.last_path):
			last_path = os.path.dirname(self.last_path)
		self.readFileList(last_path)

	def readFileList(self, path):
		#print("MDC: FileList: readFileList: path: %s" % path)
		self.busy = True
		self.current_path = path
		self.dir_stack.append(self.current_path)
		self.hideTiles()
		self.getFileList()

	def readFileListCallback(self):
		self.busy = False
		self.last_path = self.current_path
		#print("MDC: Cockpit: readFileListCallback: file_index: %s, path: %s, len(file_list): %s" % (self.file_index, self.file_list[self.file_index][FILE_PATH], len(self.file_list)))
		if self.file_index > -1 and self.slideshow_file_index > -1:
			self.session.openWithCallback(self.setTilesCursor, MDCPicturePlayer, self.file_list, self.slideshow_file_index, True, self.thumbnail_size)
		else:
			self.slideshow_file_index = -1
			self.paintTiles()

	def setTilesCursor(self, file_index):
		self.file_index = file_index
		self.slideshow_file_index = -1
		self.paintTiles()

### key functions

	def exit(self):
		if self.busy:
			self.cancelFileList()
		else:
			if self.file_list:
				path = self.file_list[self.file_index][FILE_PATH]
				config.plugins.mediacockpit.last_path.value = path
			config.plugins.mediacockpit.save()
			if not config.plugins.mediacockpit.tv_background.value:
				startService(self.session, self.lastservice)
			self.close()

	def red(self):
		if not self.busy:
			self.queryDeleteFile()

	def green(self):
		if not self.busy:
			self.processOk()

	def yellow(self):
		pass

	def blue(self):
		pass

	def playpause(self):
		if not self.busy:
			print("MDC-I: Cockpit: playpause")
			x = self.file_list[self.file_index]
			if x[FILE_TYPE] == TYPE_FILE:
				self.slideshow_file_index = self.file_index
				self.session.openWithCallback(self.setTilesCursor, MDCPicturePlayer, self.file_list, self.slideshow_file_index, len(self.file_list) > 1, self.thumbnail_size)
			elif x[FILE_TYPE] in [TYPE_DIR, TYPE_M3U]:
				self.slideshow_file_index = 0
				self.readFileList(x[FILE_PATH])
			elif x[FILE_TYPE] == TYPE_GOUP:
				self.prevDirectory()

	def processOk(self):
		if not self.busy:
			print("MDC-I: Cockpit: processOk")
			x = self.file_list[self.file_index]
			path = x[FILE_PATH]
			#print("MDC: Cockpit: processOk: path: %s" % path)
			if x[FILE_TYPE] == TYPE_DIR:
				self.readFileList(path)
			if x[FILE_TYPE] == TYPE_GOUP:
				self.prevDirectory()
			elif x[FILE_TYPE] == TYPE_M3U:
				self.readFileList(path)
			elif x[FILE_TYPE] == TYPE_FILE:
				if x[FILE_MEDIA] == "picture":
					self.session.openWithCallback(self.setTilesCursor, MDCPicturePlayer, self.file_list, self.file_index, False, self.thumbnail_size)
				elif x[FILE_MEDIA] == "movie":
					if config.plugins.mediacockpit.tv_background.value:
						stopService(self.session, self.lastservice)
					self.session.openWithCallback(self.MDCMoviePlayerCallback, MDCMoviePlayer, self.file_list, self.file_index)

	def MDCMoviePlayerCallback(self, _slideshow_active=False):
		if config.plugins.mediacockpit.tv_background.value:
			startService(self.session, self.lastservice)

	def prevDirectory(self):
		if not self.busy:
			#print("MDC: Cockpit: prevDirectory: last_path: %s, dir_stack: %s" % (self.last_path, str(self.dir_stack)))
			path = ""
			if self.dir_stack:
				self.last_path = self.dir_stack.pop()
				if self.dir_stack:
					self.dir_stack.pop()
			else:
				path = self.file_list[self.file_index][FILE_PATH]
				self.last_path = os.path.dirname(path)
			#print("MDC: Cockpit: prevDirectory: dir_stack: %s" % str(self.dir_stack))
			#print("MDC: Cockpit: prevDirectory: file_index: %s, path: %s, last_path: %s" % (self.file_index, path, self.last_path))
			self.readFileList(os.path.dirname(self.last_path))

	def openInfo(self):
		if not self.busy:
			if self.file_list:
				x = self.file_list[self.file_index]
				if x[FILE_TYPE] == TYPE_FILE:
					self.session.openWithCallback(self.openInfoCallback, MediaInfo, self.file_list, self.file_index)

	def openInfoCallback(self, file_index):
		self.setTilesCursor(file_index)

	def openMenu(self):
		if not self.busy:
			self.session.openWithCallback(self.openMenuCallback, ConfigScreen)

	def openMenuCallback(self, _restart=False):
		self.last_path = self.file_list[self.file_index][FILE_PATH]
		self.firstStart(False)
