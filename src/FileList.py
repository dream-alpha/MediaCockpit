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
import time
from Components.config import config
from Plugins.SystemPlugins.MountCockpit.MountCockpit import MountCockpit
from .__init__ import _
from .Version import ID
from .Debug import logger
from .MetaUtils import loadMetaFile, saveMetaFile
from .FileListUtils import FILE_IDX_PATH, FILE_IDX_DATE, FILE_IDX_TYPE, FILE_IDX_META
from .FileListUtils import FILE_TYPE_UP, FILE_TYPE_DIR, FILE_TYPE_PLAYLIST, FILE_TYPE_PICTURE, FILE_TYPE_MOVIE, FILE_TYPE_MUSIC
from .FileUtils import readFile
from .PictureUtils import getExifData, transformPicture
from .DelayTimer import DelayTimer
from .ServiceUtils import ALL_MEDIA, EXT_PICTURE, ALL_VIDEO, EXT_MUSIC, EXT_PLAYLIST
from .ConfigInit import sort_modes
from .Thumbnail import Thumbnail


class FileList(Thumbnail):

	def __init__(self):
		Thumbnail.__init__(self)
		self.file_list_sort = config.plugins.mediacockpit.sort.value
		self.recurse_dirs = config.plugins.mediacockpit.recurse_dirs.value
		self.sort_across_dirs = config.plugins.mediacockpit.sort_across_dirs.value
		self.show_dirup_tile = config.plugins.mediacockpit.show_dirup_tile.value
		self.create_thumbnails = config.plugins.mediacockpit.create_thumbnails.value
		self.show_loading_details = config.plugins.mediacockpit.show_loading_details.value
		self.home_dir = config.plugins.mediacockpit.home_dir.value
		self.playlist = None
		self.count = 0
		self.last_percent = 0
		self.total_count = 0
		self.cancelling = False
		self.percent = None
		self.path = ""
		self.bookmarks = []
		self.__callback = None

	def displayLCD(self, _title, _info):
		logger.error("overridden in child class")

	def displayOSD(self, _info):
		logger.error("overridden in child class")

	def showLoading(self, path, percent):
		if path is not None and percent is not None:
			if self.show_loading_details:
				if percent:
					adir = os.path.basename(path) if path != "/" else "/"
					self.displayOSD("%s %2d%% - %s ..." % (_("Loading"), percent, adir))
					self.displayLCD("%s %2d%%" % (_("Loading"), percent), adir)
				else:
					self.displayOSD("%s ..." % _("Initializing"))
					self.displayLCD("%s" % _("Initializing"), "...")
			else:
				self.displayOSD("%s %s ..." % (_("Loading"), _("files")))
				self.displayLCD(_("Loading"), _("files"))

	def progress(self, path):
		path = os.path.dirname(path)
		self.count += 1
		percent = int(float(self.count) / float(self.total_count) * 100) if self.total_count else 0
		logger.info("%s of %s, percent: %s", self.count, self.total_count, percent)
		if percent != self.percent or path != self.path:
			self.path = path
			self.percent = percent
			self.showLoading(path, self.percent)

	def checkFile(self, afile):
		filename, ext = os.path.splitext(os.path.basename(afile))
		return not filename.startswith(".") and (os.path.isdir(afile) or not filename.endswith((".transformed", ".thumbnail", "backdrop")) and ext.lower() in ALL_MEDIA)
		# return not filename.startswith(".") and (ext == "" or not filename.endswith((".transformed", ".thumbnail")) and ext.lower() in ALL_MEDIA)

	def listDir(self, adir):
		alist = []
		try:
			for afile in os.listdir(adir):
				path = os.path.join(adir, afile)
				if MountCockpit.getInstance().getMountPoint(ID, path):
					if self.checkFile(path):
						alist.append(path)
		except OSError as e:
			logger.error("failed: e: %s", e)
		return alist

	def countDir(self, adir):
		logger.debug("adir: %s", adir)
		count = 0
		if adir == self.home_dir:
			count = len(self.bookmarks)
		else:
			for path in self.listDir(adir):
				if os.path.isfile(path):
					count += 1
				elif os.path.isdir(path):
					if not self.playlist:
						count += 1
					else:
						count += self.countDir(path)
		logger.debug("count: %s", count)
		return count

	def countPlaylist(self, alist):
		logger.debug("alist: %s", alist)
		count = 0
		for afile in alist:
			logger.debug("afile 1: %s", afile)
			if os.path.isdir(afile) and (self.recurse_dirs and self.playlist):
				count += self.countDir(afile)
			elif os.path.isfile(afile) and self.checkFile(afile):
				logger.debug("afile 2: %s", afile)
				count += 1
		return count

	def sortList(self, file_list):
		mode, order = sort_modes[self.file_list_sort][0]
		logger.debug("sort_mode: %s, sort_order: %s", mode, order)

		if mode == "alpha":
			if self.sort_across_dirs:
				if order:
					file_list.sort(key=lambda afile: (min(afile[FILE_IDX_TYPE], FILE_TYPE_PICTURE), os.path.basename(afile[FILE_IDX_PATH]).lower()), reverse=True)
				else:
					file_list.sort(key=lambda afile: (min(afile[FILE_IDX_TYPE], FILE_TYPE_PICTURE), os.path.basename(afile[FILE_IDX_PATH]).lower()))
			else:
				if order:
					file_list.sort(key=lambda afile: (min(afile[FILE_IDX_TYPE], FILE_TYPE_PICTURE), afile[FILE_IDX_PATH].lower()), reverse=True)
				else:
					file_list.sort(key=lambda afile: (min(afile[FILE_IDX_TYPE], FILE_TYPE_PICTURE), afile[FILE_IDX_PATH].lower()))
		elif mode == "date":
			if order:
				file_list.sort(key=lambda afile: (min(afile[FILE_IDX_TYPE], FILE_TYPE_PICTURE), afile[FILE_IDX_DATE]), reverse=True)
			else:
				file_list.sort(key=lambda afile: (min(afile[FILE_IDX_TYPE], FILE_TYPE_PICTURE), afile[FILE_IDX_DATE]))
		return file_list

	def getEpochTimestamp(self, path, exif_data):
		date_time = None
		if "DateTimeOriginal" in exif_data:
			date_time = str(exif_data["DateTimeOriginal"])
		for time_format in ["%Y:%m:%d %H:%M:%S", "%m:%d:%Y %H:%M"]:
			try:
				time_tuple = time.strptime(date_time, time_format)
				time_epoch = int(time.mktime(time_tuple))
				break
			except Exception:
				# logger.debug("date_time: %s", date_time)
				stat = os.stat(path)
				time_epoch = int(stat.st_mtime)
		return time_epoch

	# Entries

	def createParentDirEntry(self, path):
		logger.debug("path: %s", path)
		afile = []
		if self.show_dirup_tile and path != self.home_dir:
			if os.path.splitext(path)[1] != ".m3u":
				path = os.path.join(path, "..")
			afile = [path, FILE_TYPE_UP, 0, {}]
		logger.debug("afile: %s", afile)
		return afile

	def createFileEntry(self, path):
		logger.debug("path: %s", path)
		afile = []
		if MountCockpit.getInstance().getMountPoint(ID, path):
			self.progress(path)
			exif_data = {}
			time_epoch = self.getEpochTimestamp(path, exif_data)
			filename, ext = os.path.splitext(path)
			if os.path.isfile(path):
				filename, ext = os.path.splitext(path)
				ext = ext.lower()
				if ext in EXT_PICTURE:
					afile = loadMetaFile(path)
					if afile:
						afile[FILE_IDX_PATH] = os.path.join(os.path.dirname(path), os.path.basename(afile[FILE_IDX_PATH]))
						exif_data = afile[FILE_IDX_META]
					else:
						exif_data = getExifData(path)
						time_epoch = self.getEpochTimestamp(path, exif_data)
						afile = [path, FILE_TYPE_PICTURE, time_epoch, exif_data]
						saveMetaFile(path, afile[:])
					if not os.path.exists(filename + ".transformed" + ext):
						transformPicture(path, exif_data["Orientation"])
					if self.create_thumbnails and not os.path.exists(filename + ".thumbnail" + ext):
						self.createThumbnail(path)
				elif ext in ALL_VIDEO:
					afile = [path, FILE_TYPE_MOVIE, time_epoch, exif_data]
				elif ext in EXT_MUSIC:
					afile = [path, FILE_TYPE_MUSIC, time_epoch, exif_data]
				elif ext in EXT_PLAYLIST:
					if not self.playlist:
						afile = [path, FILE_TYPE_PLAYLIST, time_epoch, exif_data]
			elif os.path.isdir(path):
				afile = [path, FILE_TYPE_DIR, time_epoch, exif_data]
			logger.debug("afile: %s", afile)
		return afile

	# Directory

	def scanNextDirectoryFiles(self):
		logger.debug("recurse_dirs: %s, self.todo_list: %s", self.recurse_dirs, self.todo_list)
		if self.todo_list and not self.cancelling:
			path = self.todo_list.pop(0)
			afile = self.createFileEntry(path)
			if afile:
				self.entry_list.append(afile)
			DelayTimer(1, self.scanNextDirectoryFiles)
		else:
			if self.entry_list and not self.sort_across_dirs:
				self.entry_list = self.sortList(self.entry_list)
			logger.debug("entry_list: %s", self.entry_list)
			self.file_list += self.entry_list
			self.scanNextDirectory()

	def scanDirectoryFiles(self, adir):
		logger.debug("adir: %s, recurse_dirs: %s", adir, self.recurse_dirs)
		self.todo_list = []
		self.entry_list = []
		dir_list = []
		alist = []
		if adir == self.home_dir:
			for bdir in self.bookmarks:
				if os.path.exists(bdir):
					alist.append(bdir)
		else:
			alist = self.listDir(adir)
		logger.debug("alist: %s", alist)
		for path in alist:
			if self.playlist and self.recurse_dirs and os.path.isdir(path):
				dir_list.append(path)
			else:
				self.todo_list.append(path)
		dir_list.sort()
		logger.debug("dir_list: %s", dir_list)
		logger.debug("self.todo_list: %s", self.todo_list)
		self.dir_list += dir_list
		DelayTimer(1, self.scanNextDirectoryFiles)

	def scanNextDirectory(self):
		logger.debug("dir_list: %s", self.dir_list)
		if self.dir_list and not self.cancelling:
			path = self.dir_list.pop(0)
			if os.path.isdir(path) or not self.playlist:
				logger.debug("dir: path: %s", path)
				DelayTimer(1, self.scanDirectoryFiles, path)
			else:
				logger.debug("file: path: %s", path)
				afile = self.createFileEntry(path)
				if afile:
					self.file_list.append(afile)
				DelayTimer(1, self.scanNextDirectory)
		else:
			if self.file_list and self.sort_across_dirs:
				self.file_list = self.sortList(self.file_list)
			self.cancelling = False
			logger.debug("file_list: %s", self.file_list)
			logger.debug("done.")
			self.__callback(self.file_list, True)

	def scanDirectory(self, adir):
		logger.debug("...")
		self.file_list = []
		self.dir_list = []
		self.last_percent = 0
		self.total_count = 0

		afile = self.createParentDirEntry(adir)
		if afile:
			self.file_list.append(afile)

		if self.playlist:
			self.dir_list = self.scanPlaylistFiles(adir)
			self.total_count += self.countPlaylist(self.dir_list)
		else:
			self.dir_list.append(adir)
			self.total_count += self.countDir(adir)

		logger.debug("total_count: %s", self.total_count)
		DelayTimer(1, self.scanNextDirectory)

	# Playlist

	def scanPlaylistFiles(self, path):
		logger.debug("path: %s", path)
		file_list = []
		playlist_dir = os.path.dirname(path)
		afile = readFile(path).splitlines()
		for entry in afile:
			if entry and not entry.startswith("#"):
				logger.debug("entry: %s", entry)
				path = entry
				if not path.startswith("/"):
					path = os.path.join(playlist_dir, path)
				file_list.append(path)
		return file_list

	# FileList

	def createFileList(self, path, bookmarks, callback):
		logger.info("path: %s", path)
		self.bookmarks = bookmarks
		self.__callback = callback
		self.current_page = -1
		self.file_index = -1
		self.count = -1
		self.file_list = []
		self.playlist = False
		if path == self.home_dir or MountCockpit.getInstance().getMountPoint(ID, path):
			self.playlist = os.path.splitext(path)[1] == ".m3u"
			self.progress(path)
			DelayTimer(10, self.scanDirectory, path)
		else:
			afile = self.createParentDirEntry(path)
			if afile:
				self.file_list.append(afile)
			self.__callback(self.file_list, False)

	def cancelFileList(self):
		self.cancelling = True
