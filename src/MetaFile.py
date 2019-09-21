#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2019 by dream-alpha
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
#

import os
import cPickle
from FileUtils import readFile, writeFile, deleteFile

class MetaFile(object):

	def saveMeta(self, path, meta):
		#print("MDC: MetaFile: saveMeta: path: %s, meta: %s" % (path, str(meta)))
		if meta:
			filename, _ext = os.path.splitext(path)
			meta_path = filename + ".meta"
			if os.path.exists(meta_path):
				deleteFile(meta_path)
			if not os.path.exists(meta_path):
				text = cPickle.dumps(meta)
				writeFile(meta_path, text)

	def loadMeta(self, path):
		#print("MDC: MetaFile: loadMeta: path: %s" % path)
		filename, _ext = os.path.splitext(path)
		meta_path = filename + ".meta"
		x = []
		if os.path.isfile(meta_path):
			text = readFile(meta_path)
			x = cPickle.loads(text)
		return x
