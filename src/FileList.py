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
import time
from __init__ import _
from globals import FILE_PATH, FILE_DATE, FILE_TYPE, FILE_META
from globals import TYPE_GOUP, TYPE_DIR, TYPE_FILE, TYPE_M3U
from FileUtils import readFile
from PictureUtils import getExifData, transformPicture, createThumbnail
from DelayTimer import DelayTimer
from MetaFile import MetaFile
from ServiceUtils import extMedia, extPicture, extVideo, extMusic, extPlaylist


class FileList(MetaFile, object):

	def __init__(self):
		self.thumbnail_size = None
		self.desktop_size = None
		self.last_path = None
		self.current_path = None
		self.show_goup_tile = None
		self.file_list_sort = None
		self.slideshow_file_index = None
		self.sort_modes = None
		self.recurse_dirs = None
		self.sort_across_dirs = None
		self.show_loading_details = None
		self.create_thumbnails = None
		self.playlist_active = None
		self.count = 0
		self.last_percent = 0
		self.total_count = 0
		self.cancelling = False
		self.percent = None
		self.path = None

	def readFileListCallback(self):
		print("MDC-E: FileList: readFileListCallback: overwritten in child class")

	def displayLCD(self, _title, _info):
		print("MDC-E: FileList: displayLCD: overwritten in child class")

	def displayOSD(self, _info, _enable=True):
		print("MDC-E: FileList: displayOSD: overwritten in child class")

	def showLoading(self, path, percent):
		if path is not None and percent is not None:
			if self.show_loading_details:
				adir = os.path.basename(self.path) if self.path != "/" else "/"
				self.displayOSD("%s %s (%s%%) ..." % (_("Loading"), adir, self.percent))
				self.displayLCD("%s: %s%%" % (_("Loading"), self.percent), adir)
			else:
				self.displayOSD("%s %s ..." % (_("Loading"), _("pictures")))
				self.displayLCD(_("Loading"), _("pictures"))

	def loading(self, dir_list):
		#print("MDC: FileList: loading: dir_list: %s" % str(dir_list))
		if dir_list:
			path = dir_list[0]
			if os.path.isdir(path) and path != self.path:
				self.path = path
				self.showLoading(self.path, self.percent)

	def progress(self):
		self.count += 1
		percent = int(float(self.count) / float(self.total_count) * 100) if self.total_count else 0
		#print("MDC-I: FileList: progress: %s of %s, percent: %s" % (self.count, self.total_count, percent))
		if percent != self.percent:
			self.percent = percent
			self.showLoading(self.path, self.percent)

	def checkFile(self, afile):
		filename, ext = os.path.splitext(os.path.basename(afile))
		return not filename.startswith(".") and (os.path.isdir(afile)
			or not filename.endswith((".transformed", ".thumbnail")) and ext.lower() in extMedia)
#		return not filename.startswith(".") and (ext == ""
#			or not filename.endswith((".transformed", ".thumbnail")) and ext.lower() in extMedia)

	def listDir(self, adir):
		alist = []
		try:
			for afile in os.listdir(adir):
				path = os.path.join(adir, afile)
				if self.checkFile(path):
					alist.append(path)
		except OSError as e:
			print("MDC-E: FileList: listDir: failed: e: %s" % e)
		return alist

	def countDir(self, path):
		#print("MDC: FileList: countDir: %s" % path)
		count = 0
		for adir in self.listDir(path):
			#print("MDC: FileList: countDir: %s" % adir)
			if os.path.isfile(adir):
				#print("MDC: FileList: countDir 1: %s" % adir)
				count += 1
			elif os.path.isdir(adir):
				if not self.playlist_active:
					#print("MDC: FileList: countDir 2: %s" % adir)
					count += 1
				else:
					count += self.countDir(adir)
		return count

	def countPlaylist(self, alist):
		#print("MDC: FileList: countPlaylist: alist: %s" % str(alist))
		count = 0
		for afile in alist:
			#print("MDC: FileList: countPlaylist: afile: %s" % afile)
			if os.path.isdir(afile) and (self.recurse_dirs and self.playlist_active):
				count += self.countDir(afile)
			elif os.path.isfile(afile) and self.checkFile(afile):
				#print("MDC: FileList: countPlaylist 2: afile: %s" % afile)
				count += 1
		return count

	def sortList(self, file_list):
		mode, order = self.sort_modes[self.file_list_sort][0]
		#print("MDC: Filelist: sortList: sort_mode: %s, sort_order: %s" % (mode, order))

		if mode == "alpha":
			if self.sort_across_dirs:
				if order:
					file_list.sort(key=lambda x: (x[FILE_TYPE], os.path.basename(x[FILE_PATH]).lower()), reverse=True)
				else:
					file_list.sort(key=lambda x: (x[FILE_TYPE], os.path.basename(x[FILE_PATH]).lower()))
			else:
				if order:
					file_list.sort(key=lambda x: (x[FILE_TYPE], x[FILE_PATH].lower()), reverse=True)
				else:
					file_list.sort(key=lambda x: (x[FILE_TYPE], x[FILE_PATH].lower()))
		elif mode == "date":
			if order:
				file_list.sort(key=lambda x: (x[FILE_TYPE], x[FILE_DATE]), reverse=True)
			else:
				file_list.sort(key=lambda x: (x[FILE_TYPE], x[FILE_DATE]))
		return file_list

	def restoreLastFileEntry(self):
		#print("MDC: FileList: restoreLastFileEntry: len(self.file_list): %s, last_path: %s" % (len(self.file_list), self.last_path))
		self.file_index = -1
		if self.file_list and self.last_path:
			#print("MDC: FileList: restoreLastFileEntry: self.file_list: %s" % str(self.file_list))
			self.file_index = 0
			for index, x in enumerate(self.file_list):
				#print("MDC: FileList: restoreLastFileEntry index: %s, x: %s, last_path: %s" % (index, str(x), self.last_path))
				if x[FILE_PATH] == self.last_path:
					self.file_index = index
					break

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
				#print("MCD: FileList: getEpochTimestamp: date_time: %s" % date_time)
				stat = os.stat(path)
				time_epoch = int(stat.st_mtime)
		return time_epoch

	### Entries

	def createParentDirEntry(self, path):
		#print("MDC: FileList: createParentDirEntry: path: %s" % path)
		x = []
		if "goup" in self.filefilters:
			self.progress()
			x = [path, TYPE_GOUP, 0, "goup", {}]
		return x

	def createFileEntry(self, path):
		#print("MDC: FileList: createFileEntry: path: %s" % path)
		path = os.path.realpath(path)

		x = []
		filetype = None
		exif_data = {}
		time_epoch = 0
		filefilter = 0

		self.progress()
		_filename, ext = os.path.splitext(path)
		if os.path.isfile(path):
			if "picture" in self.filefilters and ext.lower() in extPicture:
				x = self.loadMeta(path)
				if x:
					exif_data = x[FILE_META]
				else:
					filefilter = TYPE_FILE
					filetype = "picture"
					if not self.cancelling:
						exif_data = getExifData(path)
						time_epoch = self.getEpochTimestamp(path, exif_data)
						#print("MCD: FileList: createFileEntry: path: %s, date_time: %s, time_epoch: %s" % (path, date_time, time_epoch))
						transformPicture(path, exif_data["Orientation"])
						if self.create_thumbnails:
							createThumbnail(path, (self.thumbnail_size.width(), self.thumbnail_size.height()))
			elif "movie" in self.filefilters and ext.lower() in extVideo:
				filefilter = TYPE_FILE
				filetype = "movie"
			elif "music" in self.filefilters and ext.lower() in extMusic:
				filefilter = TYPE_FILE
				filetype = "music"
			elif "playlist" in self.filefilters and ext.lower() in extPlaylist:
				if not self.playlist_active:
					filefilter = TYPE_M3U
					filetype = "playlist"
		elif os.path.isdir(path):
			if "folder" in self.filefilters:
				filefilter = TYPE_DIR
				filetype = "folder"

		if not x and filetype:
			x = [path, filefilter, time_epoch, filetype, exif_data]
			#print("MDC: FileList: createDirectoryxEntry: x: %s" % str(x))
			if filetype in ["picture"] and not self.cancelling:
				self.saveMeta(path, x)
		return x

	### Directory

	def scanNextDirectoryFiles(self):
		#print("MDC: FileList: scanNextDirectoryFiles: recurse_dirs: %s, self.todo_list: %s" % (self.recurse_dirs, str(self.todo_list)))
		if self.todo_list:
			path = self.todo_list.pop(0)
			x = self.createFileEntry(path)
			if x:
				self.entry_list.append(x)
			#self.progress()
			DelayTimer(1, self.scanNextDirectoryFiles)
		else:
			if self.entry_list and not self.sort_across_dirs:
				self.entry_list = self.sortList(self.entry_list)

			#print("MDC: FileList: scanNextDirectoryFiles: entry_list: %s" % str(self.entry_list))
			self.file_list += self.entry_list
			self.scanNextDirectory()

	def scanDirectoryFiles(self, adir):
		#print("MDC: FileList: scanDirectoryFiles: adir: %s, recurse_dirs: %s" % (adir, self.recurse_dirs))
		self.todo_list = []
		self.entry_list = []
		dir_list = []
		alist = self.listDir(adir)
		#print("MDC: FileList: scanDirectoryFiles: alist: %s" % str(alist))
		for path in alist:
			if self.playlist_active and self.recurse_dirs and os.path.isdir(path):
				dir_list.append(os.path.realpath(path))
			else:
				self.todo_list.append(path)
		dir_list.sort()
		#print("MDC: FileList: scanDirectoryFiles: dir_list: %s" % str(dir_list))
		#print("MDC: FileList: scanDirectoryFiles: self.todo_list: %s" % str(self.todo_list))
		self.dir_list += dir_list
		DelayTimer(1, self.scanNextDirectoryFiles)

	def scanNextDirectory(self):
		#print("MDC: FileList: scanNextDirectory: dir_list: %s" % str(self.dir_list))
		if self.dir_list and not self.cancelling:
			path = self.dir_list.pop(0)
			if os.path.isdir(path) or not self.playlist_active:
				#print("MDC: FileList: scanNextDirectory: dir: path: %s" % path)
				self.loading([path])
				DelayTimer(1, self.scanDirectoryFiles, path)
			else:
				#print("MDC: FileList: scanNextDirectory: file: path: %s" % path)
				x = self.createFileEntry(path)
				if x:
					self.file_list.append(x)
				DelayTimer(1, self.scanNextDirectory)
		else:
			# done
			if self.file_list and self.sort_across_dirs:
				self.file_list = self.sortList(self.file_list)
			self.cancelling = False
			self.restoreLastFileEntry()
			self.readFileListCallback()

	def scanDirectory(self, adir):
		#print("MDC: FileList: scanDirectory")
		self.file_list = []
		self.dir_list = []
		self.last_percent = 0
		self.total_count = 0

		x = self.createParentDirEntry(os.path.join(adir, ".."))
		if x:
			self.total_count = 1
			self.file_list.append(x)

		if self.playlist_active:
			self.dir_list = self.scanPlaylistFiles(adir)
			self.total_count += self.countPlaylist(self.dir_list)
		else:
			self.dir_list.append(adir)
			self.total_count += self.countDir(adir)

		#print("MDC: FileList: scanDirectory: total_count: %s" % self.total_count)

		self.loading(self.dir_list)
		DelayTimer(1, self.scanNextDirectory)

	### Playlist

	def scanPlaylistFiles(self, path):
		#print("MDC: FileList: scanPlaylistFiles: path: %s" % path)
		file_list = []

		playlist_dir = os.path.dirname(path)
		afile = readFile(path).splitlines()
		for entry in afile:
			if entry and not entry.startswith("#"):
				#print("MDC: FileList: scanPlaylistFiles: apath: %s" % apath)
				path = entry
				if not path.startswith("/"):
					path = os.path.join(playlist_dir, path)
				file_list.append(path)
		return file_list

	### FileList

	def getFileList(self):
		print("MDC-I: FileList: getFileList: current_path: %s" % self.current_path)
		#print("MDC: FileList: getFileList: dir_stack: %s" % str(self.dir_stack))
		self.current_page = -1
		self.file_index = -1
		self.count = -1
		self.playlist_active = False
		self.filefilters = ["goup"] if self.show_goup_tile else []
		if os.path.splitext(self.current_path)[1] == ".m3u":
			self.playlist_active = True
			self.filefilters += ["picture", "movie"]
		else:
			if self.slideshow_file_index > -1:
				self.filefilters += ["picture", "movie"]
			else:
				self.filefilters += ["folder", "playlist", "picture", "movie"]
		self.loading([self.current_path])
		self.progress()
		DelayTimer(10, self.scanDirectory, self.current_path)

	def cancelFileList(self):
		self.cancelling = True
