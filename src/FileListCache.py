#!/usr/bin/python
# encoding: utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
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


from Components.config import config
from .Debug import logger
from .FileList import FileList
from .MetaUtils import existsMetaList, getMetaList, deleteMetaList, saveMetaList


class FileListCache(FileList):

	def __init__(self):
		self.__path = None
		self.__callback = None
		FileList.__init__(self)

	def getFileList(self, path, bookmarks, callback):
		logger.info("path: %s, callback: %s", path, callback)
		self.__path = path
		self.__callback = callback
		file_list = []
		if config.plugins.mediacockpit.cache.value and existsMetaList(path):
			file_list = getMetaList(path)
			self.__callback(file_list, True)
		else:
			self.createFileList(path, bookmarks, self.getFileListCallback)

	def getFileListCallback(self, file_list, is_mounted):
		logger.info("path: %s", self.__path)
		if config.plugins.mediacockpit.cache.value and self.__path != config.plugins.mediacockpit.home_dir.value:
			saveMetaList(self.__path, file_list)
		self.__callback(file_list, is_mounted)

	def saveMetaList(self, path, file_list):
		saveMetaList(path, file_list)

	def deleteMetaList(self, path):
		deleteMetaList(path)
