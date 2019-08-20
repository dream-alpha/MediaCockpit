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
from Screens.MessageBox import MessageBox
from Screens.LocationBox import LocationBox
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.AVSwitch import AVSwitch
from Components.Sources.StaticText import StaticText
from Components.config import config
from enigma import getDesktop
from Picture import MDCPicturePlayer
from FileUtils import deleteFile
from globals import FILE_TYPE, FILE_PATH, FILE_MEDIA, TYPE_DIR, TYPE_FILE, TYPE_M3U, TYPE_GOUP
from FileList import FileList
from FileInfo import FileInfo
from DelayedFunction import DelayedFunction
from Tiles import Tiles


def stopService(session, lastservice):
	#print("MDC: Cockpit: stopService: clear video buffer")
	session.nav.stopService()
	session.nav.playService(lastservice)
	session.nav.stopService()


def startService(session, lastservice):
	#print("MDC: Cockpit: startService: start")
	session.nav.playService(lastservice)


class MDCSummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self.skinName = ["MDCSummary"]


class Cockpit(Tiles, FileList, HelpableScreen):

	def __init__(self, session):
		print("MDC-I: Cockpit: __init__")
		self.sc = AVSwitch().getFramebufferScale()
		self.file_list = []
		self.file_index = -1
		self.lastservice = None
		self.slideshow_active = False

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = self.getSkinName()

		self["actions"] = HelpableActionMap(
			self,
			"MDCActions",
			{
				"playpause":	(self.startSlideshow,	_("Pause/Resume") + " " + _("Slideshow")),
				"nextBouquet":	(self.prevPage,		_("Previous page")),
				"prevBouquet":	(self.nextPage,		_("Next page")),
				"right":	(self.moveRight,	_("Next picture")),
				"left":		(self.moveLeft,		_("Previous picture")),
				"up":		(self.moveUp,		_("Previous line")),
				"down":		(self.moveDown,		_("Next line")),
				"green":	(self.pressOk,		_("Ok")),
				"ok":		(self.pressOk,		_("Ok")),
				"info":		(self.openFileInfo,	_("Information")),
				"menu":		(self.openConfigScreen, _("Settings")),
				"red":		(self.queryDeleteFile,	_("Delete file")),
				"exit":		(self.exit,		_("Exit")),
				"0":		(self.press0,		_("Home")),
#				"keyNext":	(self.nextDirectory,	_("Next directory")),
				"keyPrev":	(self.prevDirectory,	_("Previous directory")),
			},
			prio=-1
		)

		self["no_support"] = Label(_("Skin resolution other than Full HD is not supported yet"))
		self["osd_info"] = Label()
		self["lcd_info"] = StaticText()
		self["lcd_title"] = StaticText()

		Tiles.__init__(self)
		self.tiles = self.getTiles()

		if config.plugins.mediacockpit.start_home_dir.value:
			self.last_path = config.plugins.mediacockpit.home_dir.value
		else:
			self.last_path = config.plugins.mediacockpit.last_path.value
		print("MDC-I: Cockpit: __init__: last_path: %s" % self.last_path)

		FileList.__init__(self)
		self.first_start = True
		self.current_path = None
		self.dir_stack = []

		animations_enabled = getDesktop(0).isAnimationsEnabled()
		print("MDC-I: Cockpit: __init__: animations_enabled: %s" % animations_enabled)
		self.onShow.append(self.onDialogShow)

	def createSummary(self):
		return MDCSummary

	def getSkinName(self):
		skin_name = "MDCCockpit"
		if getDesktop(0).size().width() != 1920:
			skin_name = "MDCNoSupport"
			self.setTitle(_("Information"))
		return skin_name

	def showLoadInfo(self, adir):
		self["osd_info"].setText(_("Loading") + " %s..." % adir)
		self["lcd_title"].setText(_("Loading") + "...")
		self["lcd_info"].setText(os.path.basename(adir))

	def onDialogShow(self):
		print("MDC: Cockpit: onDialogShow")
		if self.first_start:
			self.first_start = False
			self.initTileAttribs()
			DelayedFunction(10, self.firstStart)

	def firstStart(self, first_start=True):
		#print("MDC: Cockpit: firstStart: first_start: %s" % self.first_start)
		self.file_list_sort = config.plugins.mediacockpit.sort.value

		if not first_start:
			self.initTileAttribs()

		if first_start:
			self.lastservice = self.session.nav.getCurrentlyPlayingServiceReference()
		if not config.plugins.mediacockpit.tv_background.value:
			stopService(self.session, self.lastservice)
		else:
			startService(self.session, self.lastservice)

		self.readFileList(os.path.dirname(self.last_path))

	def readFileList(self, path):
		self.current_path = path
		self.hideTiles()
		self.showLoadInfo(self.current_path)
		DelayedFunction(25, self.readFileList2)

	def readFileList2(self):
		print("MDC-I: Cockpit: readFileList2: current_path: %s, last_path: %s" % (self.current_path, self.last_path))
		self.dir_stack.append(self.current_path)
		print("MDC: Cockpit: readFileList2: dir_stack: %s" % str(self.dir_stack))
		self.recurse_dirs = config.plugins.mediacockpit.recurse_dirs.value
		self.sort_across_dirs = config.plugins.mediacockpit.sort_across_dirs.value
		self.current_page = -1
		self.file_index = -1
		filters = ["goup"] if config.plugins.mediacockpit.show_goup_tile.value else []
		if os.path.splitext(self.current_path)[1] == ".m3u":
			filters += ["picture", "movie"]
			self.scanPlaylist(self.current_path, sort_mode=self.file_list_sort, filefilters=filters, recurse_dirs=self.recurse_dirs, sort_across_dirs=self.sort_across_dirs)
		else:
			if self.slideshow_active:
				filters += ["picture", "movie"]
			else:
				filters += ["folder", "playlist", "picture", "movie"]
			self.scanDirectory(self.current_path, sort_mode=self.file_list_sort, filefilters=filters, recurse_dirs=False, sort_across_dirs=self.sort_across_dirs)

	def readFileListCallback(self):
		if self.file_list:
			#print("MDC: Cockpit: readFileListCallback: self.file_list: %s" % str(self.file_list))
			self.file_index = 0
			if self.last_path:
				for index, x in enumerate(self.file_list):
					#print("MDC: Cockpit: readFileListCallback: x: %s, last_path: %s" % (str(x), self.last_path))
					if x[FILE_PATH] == self.last_path:
						self.file_index = index
		self.last_path = self.current_path
		print("MDC: Cockpit: readFileListCallback: file_index: %s" % self.file_index)
		if self.file_list and self.slideshow_active:
			self.session.openWithCallback(self.setTileCursor, MDCPicturePlayer, self.file_list, self.file_index, True)
		else:
			self.slideshow_active = False
			self.showTiles()


	def showTiles(self, refresh_tiles=False):
		self.paintTiles(refresh_tiles)
		self.showInfo()

	def showInfo(self):
		if self.file_list:
			x = self.file_list[self.file_index]
			path = x[FILE_PATH]
			filetype = _("File") if x[FILE_TYPE] == TYPE_FILE else _("Path")
		else:
			path = self.current_path
			filetype = _("Path")

		info = "%d/%d" % (self.file_index + 1, len(self.file_list))
		self["lcd_title"].setText(info)
		self["lcd_info"].setText(os.path.basename(path))
		self["osd_info"].setText("%s - %s: %s" % (info, filetype, path))

	def setTileCursor(self, file_index, refresh_tiles=False):
		self.file_index = file_index
		self.slideshow_active = False
		DelayedFunction(10, self.showTiles, refresh_tiles)

	def startSlideshow(self):
		#print("MDC: Cockpit: startSlideshow")
		x = self.file_list[self.file_index]
		print("MDC: Cockpit: startSlideshow: x: %s" % str(x))
		if x[FILE_TYPE] == TYPE_FILE:
			self.slideshow_active = True
			self.readFileList(os.path.dirname(x[FILE_PATH]))
		elif x[FILE_TYPE] in [TYPE_DIR, TYPE_M3U]:
			self.slideshow_active = True
			self.readFileList(x[FILE_PATH])
		elif x[FILE_TYPE] == TYPE_GOUP:
			self.prevDirectory()

	def pressOk(self):
		#print("MDC: Cockpit: pressOk")
		x = self.file_list[self.file_index]
		path = x[FILE_PATH]
		#print("MDC: Cockpit: pressOk: path: %s" % path)
		if x[FILE_TYPE] == TYPE_DIR:
			self.readFileList(path)
		if x[FILE_TYPE] == TYPE_GOUP:
			self.prevDirectory()
		elif x[FILE_TYPE] == TYPE_M3U:
			self.readFileList(path)
		elif x[FILE_TYPE] == TYPE_FILE:
			if x[FILE_MEDIA] == "picture":
				self.session.openWithCallback(self.setTileCursor, MDCPicturePlayer, self.file_list, self.file_index)
			elif x[FILE_MEDIA] == "movie":
#				if config.plugins.mediacockpit.tv_background.value:
#					stopService(self.session, self.lastservice)
				self.session.openWithCallback(self.MDCMoviePlayerCallback, MDCMoviePlayer, self.file_list, self.file_index)

	def MDCMoviePlayerCallback(self, _slideshow_active=False):
		if config.plugins.mediacockpit.tv_background.value:
			startService(self.session, self.lastservice)

	def exit(self):
		self.cancelPaintThumbnails()
		if self.file_list:
			path = self.file_list[self.file_index][FILE_PATH]
			config.plugins.mediacockpit.last_path.value = path
		config.plugins.mediacockpit.save()
		if not config.plugins.mediacockpit.tv_background.value:
			startService(self.session, self.lastservice)
		self.close()

	def press0(self):
		self.file_index = 0
		self.showTiles()

	def moveLeft(self):
		self.file_index -= 1
		if self.file_index < 0:
			self.file_index = len(self.file_list) - 1
		self.showTiles()

	def moveRight(self):
		self.file_index += 1
		if self.file_index > len(self.file_list) - 1:
			self.file_index = 0
		self.showTiles()

	def moveUp(self):
		self.file_index -= self.tile_columns
		if self.file_index < 0:
			self.file_index = len(self.file_list) - 1
		self.showTiles()

	def moveDown(self):
		self.file_index += self.tile_columns
		if self.file_index > len(self.file_list) - 1:
			self.file_index = 0
		self.showTiles()

	def nextPage(self):
		self.file_index += self.tiles
		self.file_index = self.file_index / self.tiles * self.tiles
		if self.file_index > len(self.file_list) - 1:
			self.file_index = 0
		self.showTiles()

	def prevPage(self):
		self.file_index -= self.tiles
		if self.file_index < 0:
			self.file_index = len(self.file_list) - 1
		self.file_index = self.file_index / self.tiles * self.tiles
		self.showTiles()

	def prevDirectory(self):
		if self.dir_stack:
			self.last_path = self.dir_stack.pop()
			next_path = os.path.dirname(self.last_path)
			if self.dir_stack:
				self.dir_stack.pop()
		else:
			x = self.file_list[self.file_index]
			path = x[FILE_PATH]
			self.last_path = os.path.dirname(path)
			next_path = os.path.dirname(self.last_path)
		print("MDC: Cockpit: prevDirectory: dir_stack: %s" % str(self.dir_stack))
		self.readFileList(next_path)

# 	def nextDirectory(self):
# 		return

	def openFileInfo(self):
		if self.file_list:
			x = self.file_list[self.file_index]
			if x[FILE_TYPE] & TYPE_FILE:
				self.session.openWithCallback(self.openFileInfoCallback, FileInfo, self.file_list, self.file_index)

	def openFileInfoCallback(self, reload_tiles, file_index):
		if reload_tiles:
			self.current_page = -1
		self.setTileCursor(file_index)

	def openConfigScreen(self):
		self.session.openWithCallback(self.openConfigScreenCallback, ConfigScreen)

	def openConfigScreenCallback(self, _restart=False):
		self.last_path = self.file_list[self.file_index][FILE_PATH]
		self.firstStart(False)

	def queryDeleteFile(self):
		self.session.openWithCallback(self.queryDeleteFileCallback, MessageBox, _("Do you really want to delete the file?"))

	def queryDeleteFileCallback(self, answer=None):
		if answer:
			filename, ext = os.path.splitext(self.file_list[self.file_index][FILE_PATH])
			deleteFile(filename + ext)
			deleteFile(filename + ".rotated" + ext)
			deleteFile(filename + ".thumbnail" + ext)
			deleteFile(filename + ".scaled" + ext)
			self.file_index += 1
			if self.file_index > len(self.file_list) - 1:
				self.file_index = len(self.file_list) - 1
			self.last_path = self.file_list[self.file_index][FILE_PATH]
			self.readFileList(self.current_path)

	def selectDirectory(self, callback, title, current_dir):
		self.session.openWithCallback(
			callback,
			LocationBox,
			windowTitle=title,
			text=_("Select directory"),
			currDir=current_dir,
			bookmarks=config.plugins.mediacockpit.media_dirs,
			autoAdd=False,
			editDir=True,
			inhibitDirs=["/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/usr", "/var"],
			minFree=100
		)
