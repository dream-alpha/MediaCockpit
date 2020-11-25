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


import os
from __init__ import _
from ConfigScreen import ConfigScreen
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.ActionMap import HelpableActionMap
from Components.config import config
from enigma import getDesktop
from MetaFile import FILE_TYPE, FILE_PATH, FILE_MEDIA, TYPE_DIR, TYPE_FILE, TYPE_M3U, TYPE_GOUP
from FileList import FileList
from FileListUtils import getIndex
from MediaInfo import MediaInfo
from DelayTimer import DelayTimer
from Tiles import Tiles
from FileOps import FileOps
from ConfigInit import sort_modes
from Display import Display
from MediaPlayer import MDCMediaPlayer
from MusicPlayer import MDCMusicPlayer
from VideoPlayer import MDCVideoPlayer
from ServiceUtils import getService, startService, stopService


class Cockpit(Display, Tiles, FileOps, FileList, HelpableScreen, Screen):

	def __init__(self, session):
		print("MDC-I: Cockpit: __init__: session: %s" % session)
		FileList.__init__(self)

		self.file_list = []
		self.file_index = -1
		self.media_list = []
		self.media_index = -1
		self.song_list = []
		self.song_index = -1
		self.lastservice = None
		self.slideshow = False
		self.thumbnail_size = None
		self.sort_modes = sort_modes
		self.load_path = None
		self.busy = False

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		Display.__init__(self)
		Tiles.__init__(self)
		FileOps.__init__(self, session)

		self.desktop_size = getDesktop(0).size()
		self.skinName = self.getSkinName()

		self["actions"] = HelpableActionMap(
			self,
			"MDCActions",
			{
				"playpause":	(self.playpause,	_("Play/Pause") + " " + _("Slideshow")),
				"nextBouquet":	(self.prevPage,		_("Previous page")),
				"prevBouquet":	(self.nextPage,		_("Next page")),
				"right":	(self.moveRight,	_("Next picture")),
				"left":		(self.moveLeft,		_("Previous picture")),
				"up":		(self.moveUp,		_("Previous row")),
				"down":		(self.moveDown,		_("Next row")),
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
			stopService(self.session, self.lastservice)

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
		self.getFileList(self.current_path)

	def readFileListCallback(self, is_mounted):
		self.busy = False
		self.last_path = self.current_path
		#print("MDC: Cockpit: readFileListCallback: file_index: %s, path: %s, len(file_list): %s" % (self.file_index, self.file_list[self.file_index][FILE_PATH], len(self.file_list)))
		#print("MDC: Cockpit: readFileListCallback: media_index: %s, song_index: %s" % (self.media_index, self.song_index))

		if self.slideshow:
			self.startSlideshow()
		else:
			self.paintTiles(is_mounted)

	def startSlideshow(self):
		self.hide()
		start_path = self.file_list[self.file_index][FILE_PATH] if self.file_list else ""
		if self.media_list and self.file_list[self.file_index][FILE_MEDIA] in ["picture", "movie"]:
			self.media_index = getIndex(self.media_list, start_path)
			self.session.openWithCallback(self.MDCMediaPlayerCallback, MDCMediaPlayer, self.media_list, self.media_index, self.slideshow, self.thumbnail_size, self.lastservice, self.song_list)
		elif self.song_list:
			self.song_index = getIndex(self.song_list, start_path)
			self.session.openWithCallback(self.MDCMusicPlayerCallback, MDCMusicPlayer, self.song_list, self.song_index)

	def MDCMediaPlayerCallback(self, path):
		# clear video buffer
		startService(self.session, self.lastservice)
		stopService(self.session, self.lastservice)
		self.setTilesCursor(getIndex(self.file_list, path))

	def MDCVideoPlayerCallback(self, _reopen=False):
		# clear video buffer
		startService(self.session, self.lastservice)
		stopService(self.session, self.lastservice)
		self.setTilesCursor(self.file_index)

	def MDCMusicPlayerCallback(self, path):
		self.setTilesCursor(getIndex(self.file_list, path))

	def setTilesCursor(self, file_index):
		self.show()
		self.file_index = file_index
		self.slideshow = False
		self.paintTiles(True)

### key functions

	def exit(self):
		if self.busy:
			self.cancelFileList()
		else:
			if self.file_list:
				path = self.file_list[self.file_index][FILE_PATH]
				config.plugins.mediacockpit.last_path.value = path
			config.plugins.mediacockpit.save()
			startService(self.session, self.lastservice)
			self.close()

	def red(self):
		if not self.busy:
			self.queryDeleteFile()

	def green(self):
		if not self.busy:
			self.processOk()

	def playpause(self):
		if not self.busy and self.file_list:
			self.slideshow = True
			x = self.file_list[self.file_index]
			print("MDC-I: Cockpit: playpause: x: %s" % str(x))
			if x[FILE_TYPE] == TYPE_FILE:
				self.startSlideshow()
			elif x[FILE_TYPE] in [TYPE_DIR, TYPE_M3U]:
				self.readFileList(x[FILE_PATH])
			elif x[FILE_TYPE] == TYPE_GOUP:
				self.prevDirectory()

	def processOk(self):
		if not self.busy and self.file_list:
			self.slideshow = False
			x = self.file_list[self.file_index]
			path = x[FILE_PATH]
			print("MDC-I: Cockpit: processOk: path: %s" % path)
			if x[FILE_TYPE] == TYPE_DIR:
				self.readFileList(path)
			if x[FILE_TYPE] == TYPE_GOUP:
				self.prevDirectory()
			elif x[FILE_TYPE] == TYPE_M3U:
				self.readFileList(path)
			elif x[FILE_TYPE] == TYPE_FILE:
				self.hide()
				if x[FILE_MEDIA] == "picture":
					media_index = getIndex(self.media_list, path)
					self.session.openWithCallback(self.MDCMediaPlayerCallback, MDCMediaPlayer, self.media_list, media_index, False, self.thumbnail_size)
				elif x[FILE_MEDIA] == "movie":
					self.session.openWithCallback(self.MDCVideoPlayerCallback, MDCVideoPlayer, getService(self.file_list[self.file_index][FILE_PATH]), False)
				elif x[FILE_MEDIA] == "music":
					song_index = getIndex(self.song_list, path)
					self.session.openWithCallback(self.MDCMusicPlayerCallback, MDCMusicPlayer, self.song_list, song_index)

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
		if not self.busy and self.file_list:
			x = self.file_list[self.file_index]
			if x[FILE_TYPE] == TYPE_FILE:
				self.session.openWithCallback(self.setTilesCursor, MediaInfo, self.file_list, self.file_index)

	def openMenu(self):
		if not self.busy:
			self.session.openWithCallback(self.openMenuCallback, ConfigScreen)

	def openMenuCallback(self, _restart=False):
		self.last_path = self.file_list[self.file_index][FILE_PATH]
		self.firstStart(False)
