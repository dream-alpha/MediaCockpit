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


import os
import glob
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Components.ActionMap import HelpableActionMap
from Components.config import config
from Components.Sources.StaticText import StaticText
from Components.Label import Label
from enigma import getDesktop
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from .__init__ import _
from .Version import ID, PLUGIN
from .Debug import logger
from .FileListUtils import FILE_IDX_TYPE, FILE_IDX_PATH
from .FileListUtils import FILE_TYPE_FILE, FILE_TYPE_UP, FILE_TYPE_DIR, FILE_TYPE_PLAYLIST, FILE_TYPE_PICTURE, FILE_TYPE_MOVIE, FILE_TYPE_MUSIC
from .FileListUtils import getIndex, nextIndex, splitMediaSongList
from .FileListCache import FileListCache
from .FileUtils import deleteFile, deleteFiles
from .MediaInfo import MediaInfo
from .DelayTimer import DelayTimer
from .Tiles import Tiles
from .Slideshow import Slideshow
from .ConfigScreen import ConfigScreen
from .CockpitContextMenu import CockpitContextMenu
from .MusicPlayer import CockpitMusicPlayer
from .CockpitPlayer import CockpitPlayer
from .SkinUtils import getSkinName
from .ServiceUtils import getService
from .ServiceCenter import ServiceCenter


class CockpitDisplaySummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self.skinName = ID + self.__class__.__name__


class MediaCockpit(Tiles, FileListCache, HelpableScreen, Screen):

	def __init__(self, session):
		logger.info("session: %s", session)
		self.file_list = []
		self.file_index = -1
		self.media_list = []
		self.media_index = -1
		self.song_list = []
		self.song_index = -1
		self.last_service = None
		self.slideshow = False
		self.busy = False
		self.cancel_request = False
		self.bookmarks = []
		self.first_start = True
		self.current_dir = None
		self.service_center = ServiceCenter()

		self["osd_info"] = Label()
		self["lcd_info"] = StaticText()
		self["lcd_title"] = StaticText()

		self["no_support"] = Label()

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		Tiles.__init__(self, self)
		FileListCache.__init__(self)

		self.desktop_size = getDesktop(0).size()
		self.skinName = getSkinName(self.__class__.__name__)

		self["actions"] = HelpableActionMap(
			self,
			"CockpitActions",
			{
				"PLAY":		(self.playpause,	_("Play/Pause") + " " + _("Slideshow")),
				"CHANNELUPR":	(self.prevPage,		_("Previous page")),
				"CHANNELDOWNR":	(self.nextPage,		_("Next page")),
				"RIGHTR":	(self.moveRight,	_("Next picture")),
				"LEFTR":	(self.moveLeft,		_("Previous picture")),
				"UPR":		(self.moveUp,		_("Previous row")),
				"DOWNR":	(self.moveDown,		_("Next row")),
				"OK":		(self.processOk,	_("Ok")),
				"INFO":		(self.openInfo,		_("Information")),
				"MENU":		(self.openContextMenu, 	_("Context menu")),
				"RED":		(self.deleteFile,	_("Delete file")),
				"GREEN":	(self.goHome,		_("Home")),
				"YELLOW":	(self.reloadFiles,	_("Reload files")),
				"BLUE":		(self.openBookmarks,	_("Bookmarks")),
				"EXIT":		(self.exit,		_("Exit")),
				"POWER":	(self.exit,		_("Exit")),
				"0":		(self.moveTop,		_("Start of list")),
				"PREVIOUS":	(self.goUp,		_("Previous directory")),
			},
			prio=-1
		)

		self.home_dir = config.plugins.mediacockpit.home_dir.value
		self.last_path = config.plugins.mediacockpit.last_path.value
		if config.plugins.mediacockpit.start_home_dir.value:
			self.last_path = self.home_dir
		logger.info("last_path: %s", self.last_path)

		animations_enabled = getDesktop(0).isAnimationsEnabled()
		logger.info("animations_enabled: %s", animations_enabled)

		self.setTitle(PLUGIN)
		self.onShow.append(self.onDialogShow)

	def displayLCD(self, title, info):
		# logger.debug("title: %s, info: %s", title, info)
		self["lcd_title"].setText(title)
		self["lcd_info"].setText(info)

	def displayOSD(self, info):
		# logger.debug("info: %s", info)
		self["osd_info"].setText(_("MediaCockpit") + " - " + info)

	def createSummary(self):
		return CockpitDisplaySummary

	def onDialogShow(self):
		logger.info("...")
		if self.first_start:
			self.first_start = False
			self.bookmarks = config.plugins.mediacockpit.bookmarks.value
			self.last_service = self.session.nav.getCurrentlyPlayingServiceReference()
			self.stopService(self.session, self.last_service)
			DelayTimer(10, self.firstStart)

	def firstStart(self):
		logger.info("...")
		self.initTileAttribs()
		adir = self.home_dir if self.last_path in self.bookmarks else os.path.dirname(self.last_path)
		self.readFileList(adir)

	def readFileList(self, adir):
		logger.debug("adir: %s", adir)
		self.hideTiles()
		self.busy = True
		self.current_dir = adir
		self.getFileList(adir, self.bookmarks, self.readFileListCallback)

	def readFileListCallback(self, file_list, is_mounted=True):
		self.file_list = file_list
		self.busy = self.cancel_request = False
		self.media_list, self.song_list = splitMediaSongList(self.file_list)
		self.file_index = getIndex(self.file_list, self.last_path)
		self.last_path = self.current_dir
		if self.file_index >= 0:
			logger.debug("file_index: %s, path: %s, len(file_list): %s", self.file_index, self.file_list[self.file_index][FILE_IDX_PATH], len(self.file_list))
		logger.debug("media_index: %s, song_index: %s", self.media_index, self.song_index)

		if self.slideshow:
			self.startSlideshow()
		else:
			self.paintTiles(is_mounted)

	def goUp(self):
		if not self.busy and self.current_dir != self.home_dir:
			logger.debug("current_dir: %s", self.current_dir)
			self.last_path = self.current_dir
			adir = self.home_dir if self.current_dir in self.bookmarks else os.path.dirname(self.current_dir)
			self.readFileList(adir)

	def startSlideshow(self):
		self.hide()
		start_path = self.file_list[self.file_index][FILE_IDX_PATH] if self.file_list else ""
		if self.media_list and self.file_list[self.file_index][FILE_IDX_TYPE] in [FILE_TYPE_PICTURE, FILE_TYPE_MOVIE]:
			self.media_index = getIndex(self.media_list, start_path)
			self.session.openWithCallback(self.SlideshowCallback, Slideshow, self.media_list, self.media_index, self.slideshow, self.song_list)
		elif self.song_list:
			self.song_index = getIndex(self.song_list, start_path)
			self.session.openWithCallback(self.CockpitMusicPlayerCallback, CockpitMusicPlayer, self.song_list, self.song_index)

	def SlideshowCallback(self, path):
		# clear video buffer
		self.startService(self.session, self.last_service)
		self.stopService(self.session, self.last_service)
		self.setTilesCursor(getIndex(self.file_list, path))

	def CockpitPlayerCallback(self, _reopen=False):
		# clear video buffer
		self.startService(self.session, self.last_service)
		self.stopService(self.session, self.last_service)
		self.setTilesCursor(self.file_index)

	def CockpitMusicPlayerCallback(self, path):
		self.setTilesCursor(getIndex(self.file_list, path))

	def setTilesCursor(self, file_index):
		self.show()
		self.file_index = file_index
		self.slideshow = False
		self.paintTiles(True)

	def exit(self):
		logger.info("busy: %s", self.busy)
		if self.busy:
			self.cancel_request = True
			self.cancelFileList()
		else:
			if self.file_list:
				path = self.file_list[self.file_index][FILE_IDX_PATH]
				config.plugins.mediacockpit.last_path.value = path
				config.plugins.mediacockpit.save()
			self.startService(self.session, self.last_service)
			self.close()

	def deleteFile(self):
		if not self.busy:
			self.session.openWithCallback(self.deleteFileCallback, MessageBox, _("Do you really want to delete the file?"))

	def deleteFileCallback(self, answer=None):
		if answer:
			afile = self.file_list[self.file_index]
			path = afile[FILE_IDX_PATH]
			filename = os.path.splitext(path)[0]
			logger.debug("filename: %s", filename)
			if afile[FILE_IDX_TYPE] in FILE_TYPE_FILE:
				deleteFiles(filename + ".*")
				del self.file_list[self.file_index]
				self.saveMetaList(os.path.dirname(path), self.file_list)
				if self.file_index < len(self.file_list):
					self.last_path = self.file_list[self.file_index][FILE_IDX_PATH]
				else:
					self.last_path = self.current_dir
				self.paintTiles()
			else:
				logger.info("%s not a file", afile[FILE_IDX_PATH])

	def goHome(self):
		self.readFileList(self.home_dir)

	def reloadFiles(self):
		if not self.busy:
			self.session.openWithCallback(self.reloadFilesCallback, MessageBox, _("Do you really want to reload the media files?"))

	def reloadFilesCallback(self, answer=None):
		if answer:
			# delete meta list
			self.deleteMetaList(self.current_dir)
			# delete all meta files
			for afile in self.file_list:
				path = afile[FILE_IDX_PATH]
				filename, _ext = os.path.splitext(path)
				for path2 in glob.glob(filename + ".*"):
					filename2, ext2 = os.path.splitext(path2)
					if filename2.endswith((".rotated", ".scaled", ".thumbnail", ".transformed")) or ext2 in [".media"]:
						print("removing: %s" % path2)
						deleteFile(path2)
			self.readFileList(self.current_dir)

	def playpause(self):
		if not self.busy and self.file_list:
			self.slideshow = True
			afile = self.file_list[self.file_index]
			logger.info("afile: %s", afile)
			if afile[FILE_IDX_TYPE] in FILE_TYPE_FILE:
				self.startSlideshow()
			elif afile[FILE_IDX_TYPE] == FILE_TYPE_UP:
				self.file_index = nextIndex(self.file_index, len(self.file_list))
				self.startSlideshow()
			elif afile[FILE_IDX_TYPE] in [FILE_TYPE_DIR, FILE_TYPE_PLAYLIST]:
				self.readFileList(afile[FILE_IDX_PATH])
			else:
				self.slideshow = False

	def processOk(self):
		if not self.busy and self.file_list:
			self.slideshow = False
			afile = self.file_list[self.file_index]
			path = afile[FILE_IDX_PATH]
			logger.info("path: %s", path)
			if afile[FILE_IDX_TYPE] == FILE_TYPE_DIR:
				self.readFileList(path)
			if afile[FILE_IDX_TYPE] == FILE_TYPE_UP:
				self.goUp()
			elif afile[FILE_IDX_TYPE] == FILE_TYPE_PLAYLIST:
				self.readFileList(path)
			elif afile[FILE_IDX_TYPE] in FILE_TYPE_FILE:
				self.hide()
				if afile[FILE_IDX_TYPE] == FILE_TYPE_PICTURE:
					media_index = getIndex(self.media_list, path)
					self.session.openWithCallback(self.SlideshowCallback, Slideshow, self.media_list, media_index, False)
				elif afile[FILE_IDX_TYPE] == FILE_TYPE_MOVIE:
					self.session.openWithCallback(self.CockpitPlayerCallback, CockpitPlayer, getService(self.file_list[self.file_index][FILE_IDX_PATH]), config.plugins.mediacockpit, True, 0, None, self.service_center)
				elif afile[FILE_IDX_TYPE] == FILE_TYPE_MUSIC:
					song_index = getIndex(self.song_list, path)
					self.session.openWithCallback(self.CockpitMusicPlayerCallback, CockpitMusicPlayer, self.song_list, song_index, self.service_center)

	def openInfo(self):
		if not self.busy and self.file_list:
			afile = self.file_list[self.file_index]
			if afile[FILE_IDX_TYPE] in FILE_TYPE_FILE:
				self.session.openWithCallback(self.setTilesCursor, MediaInfo, self.file_list, self.file_index)

	def openConfigScreen(self):
		logger.info("...")
		self.session.openWithCallback(self.openConfigScreenCallback, ConfigScreen, config.plugins.mediacockpit)

	def openConfigScreenCallback(self, _restart=False):
		self.last_path = None
		if self.file_list:
			self.last_path = self.file_list[self.file_index][FILE_IDX_PATH]
		self.firstStart()

	def openContextMenu(self):
		if not self.busy:
			self.session.open(
				CockpitContextMenu,
				self,
			)

	def selectDirectory(self, callback, title):
		logger.debug("bookmarks: %s", config.plugins.mediacockpit.bookmarks.value)
		self.session.openWithCallback(
			callback,
			LocationBox,
			windowTitle=title,
			text=_("Select directory"),
			currDir=self.home_dir,
			bookmarks=config.plugins.mediacockpit.bookmarks,
			autoAdd=False,
			editDir=True,
			inhibitDirs=["/bin", "/boot", "/dev", "/etc", "/home", "/lib", "/proc", "/run", "/sbin", "/sys", "/usr", "/var"],
			minFree=None
		)

	def openBookmarks(self):
		self.selectDirectory(
			self.openBookmarksCallback,
			_("Bookmarks")
		)

	def openBookmarksCallback(self, path):
		logger.info("path: %s", path)
		self.bookmarks = []
		for bookmark in config.plugins.mediacockpit.bookmarks.value:
			self.bookmarks.append(os.path.normpath(bookmark))
		config.plugins.mediacockpit.bookmarks.value = self.bookmarks[:]
		config.plugins.mediacockpit.bookmarks.save()
		MountCockpit.getInstance().registerBookmarks(ID, config.plugins.mediacockpit.bookmarks.value)
		self.readFileList(self.home_dir)

	def stopService(self, session, service):
		logger.debug("clear video buffer")
		session.nav.stopService()
		session.nav.playService(service)
		session.nav.stopService()

	def startService(self, session, service):
		logger.debug("...")
		session.nav.playService(service)
