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
from globals import FILE_PATH, FILE_DATE, FILE_TYPE
from globals import TYPE_GOUP, TYPE_DIR, TYPE_FILE, TYPE_PLS
from FileUtils import readFile
from PictureUtils import getExifData
try:
	from ConfigInit import sort_modes
	from ServiceUtils import extVideo
	from DelayedFunction import DelayedFunction
except Exception:
	import threading
	sort_modes = [(("alpha", False), "test-alpha"), (("date", False), "test-date")]
	extVideo = [".mp4", ".ts"]

class FileList(object):

	def __init__(self):
		pass

	def readFileListCallback(self):
		# dummy
		pass

	def updateInfoBar(self, _adir):
		# dummy
		pass

	def listDir(self, path):
		alist = []
		try:
			alist = os.listdir(path)
		except OSError as e:
			print("MDC-E: FileList: listDir: failed: e: %s" % e)
		return alist

	def sortList(self, file_list):
		mode, order = sort_modes[self.sort_mode][0]
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

	def createGoupEntry(self, path, filefilters=None):
		#print("MDC: FileList: createGoupEntry: path: %s" % path)
		x = None
		if "goup" in filefilters and path != "/":
			x = [os.path.join(path, ".."), TYPE_GOUP, 0, "goup", {}]
		return x

	### Directory

	def createDirectoryEntry(self, path):
		#print("MDC: FileList: createDirectoryEntry: path: %s" % path)
		path = os.path.realpath(path)
		picture_exts = [".jpg", ".jpeg", ".png"]
		movie_exts = extVideo
		playlist_exts = [".m3u"]
		music_exts = [".mp3"]

		sort_mode, _sort_order = sort_modes[self.sort_mode][0]
		x = None
		filetype = ""
		meta_data = None
		time_epoch = 0
		filefilter = 0
		ext = os.path.splitext(path)[1].lower()
		if not os.path.basename(path).startswith("."):
			if os.path.isfile(path):
				if "picture" in self.filefilters and ext in picture_exts:
					filename = os.path.splitext(path)[0]
					if not filename.endswith(".rotated") and not filename.endswith(".thumbnail") and not filename.endswith(".scaled"):
						filefilter = TYPE_FILE
						filetype = "picture"
						if sort_mode == "date":
							meta_data = getExifData(path)
							if meta_data and "DateTimeOriginal" in meta_data:
								#print("MDC: FileList: createDirectoryEntry: meta_data: %s" % str(meta_data))
								date_time = str(meta_data["DateTimeOriginal"])
								for time_format in ["%Y:%m:%d %H:%M:%S", "%m:%d:%Y %H:%M"]:
									try:
										time_tuple = time.strptime(date_time, time_format)
										time_epoch = time.mktime(time_tuple)
										break
									except ValueError:
										#print("MCD: FileList: createDirectoryEntry: date_time: %s" % date_time)
										pass
								#print("MCD: FileList: createDirectoryEntry: date_time: %s, time_epoch: %s" % (date_time, time_epoch))
				elif "movie" in self.filefilters and ext in movie_exts:
					filefilter = TYPE_FILE
					filetype = "movie"
				elif "music" in self.filefilters and ext in music_exts:
					filefilter = TYPE_FILE
					filetype = "music"
				elif "playlist" in self.filefilters and ext in playlist_exts:
					filefilter = TYPE_PLS
					filetype = "playlist"
			elif os.path.isdir(path):
				if "folder" in self.filefilters:
					filefilter = TYPE_DIR
					filetype = "folder"
		if filetype:
			x = [path, filefilter, time_epoch, filetype, meta_data]
		#print("MDC: FileList: createDirectoryxEntry: x: %s" % str(x))
		return x

	def scanDirectoryFiles(self, adir):
		#print("MDC: FileList: scanDirectoryFiles: adir: %s" % adir)
		self.updateInfoBar(adir)

		file_list = []
		dirlist = []
		alist = self.listDir(adir)
		for afile in alist:
			path = os.path.join(adir, afile)
			if self.recurse_dirs and os.path.isdir(path) and not afile.startswith("."):
				dirlist.append(os.path.realpath(path))
			else:
				x = self.createDirectoryEntry(path)
				if x is not None:
					file_list.append(x)

		if file_list and not self.sort_across_dirs:
			file_list = self.sortList(file_list)
		self.file_list += file_list

		dirlist.sort()
		self.dirlist += dirlist

		#print("dirlist: " + str(self.dirlist))
		#print("file_list: " + str(self.file_list))

	def scanNextDirectory(self):
		if self.dirlist:
			adir = self.dirlist.pop(0)
			self.scanDirectoryFiles(adir)
			try:
				DelayedFunction(10, self.scanNextDirectory)
			except Exception:
				timer = threading.Timer(0.01, self.scanNextDirectory)
				timer.start()
		else:
			# done
			if self.file_list and self.sort_across_dirs:
				self.file_list = self.sortList(self.file_list)
			self.readFileListCallback()

	def scanDirectory(self, adir, filefilters=None, sort_mode=None, recurse_dirs=False, sort_across_dirs=False):
		self.filefilters = filefilters
		if self.filefilters is None:
			self.filefilters = []
		self.sort_mode = sort_mode
		self.recurse_dirs = recurse_dirs
		self.sort_across_dirs = sort_across_dirs
		self.file_list = []
		self.dirlist = []

		x = self.createGoupEntry(adir, filefilters)
		if x is not None:
			self.file_list.append(x)

		self.scanDirectoryFiles(adir)
		self.scanNextDirectory()

	### Playlist

	def scanPlaylistFiles(self, path):
		#print("MDC: FileList: scanPlaylistFiles: path: %s" % path)
		self.updateInfoBar(path)
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

		self.playlist = file_list

	def scanNextPlaylistEntry(self):
		#print("MDC: FileList: scanNextPlaylistEntry: playlist: %s" % str(self.playlist))
		if self.playlist:
			path = self.playlist.pop(0)
			if os.path.isdir(path):
				#print("MDC: FileList: scanNextPlaylistEntry: dir: path: %s" % path)
				self.updateInfoBar(path)
				file_list = []
				dirlist = []
				alist = self.listDir(path)
				for afile in alist:
					path2 = os.path.join(path, afile)
					#print("MDC: FileList: scanNextPlaylistEntry: dir: path2: %s" % path2)
					if self.recurse_dirs and os.path.isdir(path2) and not afile.startswith("."):
						dirlist.append(os.path.realpath(path2))
					else:
						x = self.createDirectoryEntry(path2)
						if x is not None:
							file_list.append(x)

				if file_list and not self.sort_across_dirs:
					file_list = self.sortList(file_list)

				dirlist.sort()
				self.playlist += dirlist
				self.file_list += file_list
			else:
				#print("MDC: FileList: scanNextPlaylistEntry: file: path: %s" % path)
				x = self.createDirectoryEntry(path)
				if x is not None:
					self.file_list.append(x)

			try:
				DelayedFunction(10, self.scanNextPlaylistEntry)
			except Exception:
				timer = threading.Timer(0.01, self.scanNextPlaylistEntry)
				timer.start()
		else:
			# done
			self.readFileListCallback()

	def scanPlaylist(self, path, sort_mode=None, filefilters=None, recurse_dirs=False, sort_across_dirs=False):
		#print("MDC: FileList: scanPlaylist: path: %s, recurse_dirs: %s" % (path, recurse_dirs))
		self.sort_mode = sort_mode
		self.recurse_dirs = recurse_dirs
		self.sort_across_dirs = sort_across_dirs
		self.filefilters = filefilters
		if self.filefilters is None:
			self.filefilters = []

		self.file_list = []
		self.dirlist = []
		self.playlist = []

		x = self.createGoupEntry(path, ["goup"])
		if x is not None:
			self.file_list.append(x)

		self.scanPlaylistFiles(path)
		self.scanNextPlaylistEntry()
