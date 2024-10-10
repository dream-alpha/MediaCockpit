#!/usr/bin/python
# coding=utf-8
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


import os
from Components.config import config


# file indexes
FILE_IDX_PATH = 0
FILE_IDX_TYPE = 1
FILE_IDX_DATE = 2
FILE_IDX_META = 3


# file types (FILE_IDX_TYPE)
FILE_TYPE_UP = 0
FILE_TYPE_DIR = 1
FILE_TYPE_PLAYLIST = 2
FILE_TYPE_PICTURE = 3
FILE_TYPE_MOVIE = 4
FILE_TYPE_MUSIC = 5

FILE_TYPE_FILE = [FILE_TYPE_PICTURE, FILE_TYPE_MOVIE, FILE_TYPE_MUSIC]


def nextIndex(file_index, file_list_length):
	index = -1
	if file_list_length > 0:
		index = (file_index + 1) % file_list_length
	return index


def previousIndex(file_index, file_list_length):
	index = -1
	if file_list_length > 0:
		index = file_index - 1 if file_index else file_list_length - 1
	return index


def getIndex(file_list, path):
	file_index = 0 if file_list else -1
	for i, afile in enumerate(file_list):
		if afile[FILE_IDX_PATH] == path:
			file_index = i
			break
	return file_index


def getPath(file_list, index):
	path = ""
	if file_list:
		path = file_list[index][FILE_IDX_PATH]
	return path


def getFile(file_list, path):
	return file_list[getIndex(file_list, path)]


def os_path_dirname(path, bookmarks):
	home_dir = config.plugins.mediacockpit.home_dir.value
	adir = home_dir
	if path and path != home_dir and path not in bookmarks:
		adir = os.path.dirname(path)
	return adir


def splitMediaSongList(file_list):
	song_list = []
	media_list = []
	for afile in file_list:
		if afile[FILE_IDX_TYPE] in FILE_TYPE_FILE:
			if afile[FILE_IDX_TYPE] == FILE_TYPE_MUSIC:
				song_list.append(afile)
			else:
				media_list.append(afile)
	return media_list, song_list
