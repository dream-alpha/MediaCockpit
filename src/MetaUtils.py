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
import six.moves.cPickle as cPickle
from .Debug import logger
from .FileUtils import readFile, writeFile, deleteFile
from .FileListUtils import FILE_IDX_PATH


METALIST = ".metalist"


def saveMetaFile(path, meta):
	logger.debug("path: %s, meta: %s", path, str(meta))
	if meta:
		filename = os.path.splitext(path)[0]
		meta_path = filename + ".media"
		if not os.path.exists(meta_path):
			meta[FILE_IDX_PATH] = os.path.basename(meta[FILE_IDX_PATH])
			text = cPickle.dumps(meta)
			writeFile(meta_path, text)


def loadMetaFile(path):
	logger.debug("path: %s", path)
	filename = os.path.splitext(path)[0]
	meta_path = filename + ".media"
	meta = []
	if os.path.isfile(meta_path):
		text = readFile(meta_path)
		meta = cPickle.loads(text)
		meta[FILE_IDX_PATH] = os.path.join(os.path.dirname(path), os.path.basename(meta[FILE_IDX_PATH]))
	logger.debug("meta: %s", meta)
	return meta


def getMetaListPath(adir):
	logger.info("adir: %s", adir)
	if not os.path.exists(adir):
		adir = "/tmp"
	path = os.path.join(adir, METALIST) if os.path.isdir(adir) else adir + METALIST
	return path


def saveMetaList(adir, file_list):
	logger.info("adir: %s", adir)
	if file_list:
		path = getMetaListPath(adir)
		text = cPickle.dumps(file_list)
		writeFile(path, text)


def getMetaList(adir):
	logger.info("adir: %s", adir)
	file_list = []
	path = getMetaListPath(adir)
	if os.path.exists(path):
		text = readFile(path)
		file_list = cPickle.loads(text)
	return file_list


def deleteMetaList(adir):
	path = getMetaListPath(adir)
	if os.path.exists(path):
		deleteFile(path)


def existsMetaList(adir):
	path = getMetaListPath(adir)
	logger.debug("path: %s", path)
	return os.path.exists(path)
