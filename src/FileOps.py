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


import os
from __init__ import _
from Components.config import config
from Screens.MessageBox import MessageBox
from Screens.LocationBox import LocationBox
from MetaFile import TYPE_FILE, FILE_PATH, FILE_TYPE


class FileOps():

	def __init__(self, session):
		self.session = session
		self.file_index = -1
		self.file_list = []
		self.current_path = None

	def readFileList(self, _path):
		# dummy
		print("MDC-E: FileOps: readFileList: overwritten in child class")

	def queryDeleteFile(self):
		self.session.openWithCallback(self.queryDeleteFileCallback, MessageBox, _("Do you really want to delete the file?"))

	def queryDeleteFileCallback(self, answer=None):
		if answer:
			afile = self.file_list[self.file_index]
			filename, _ext = os.path.splitext(afile[FILE_PATH])
			#print("MDC: FileOps: queryDeleteFileCallback: filename: %s, ext: %s" % (filename, _ext))
			if afile[FILE_TYPE] == TYPE_FILE:
				os.system("rm '" + filename + "'.*")
				self.file_index += 1
				if self.file_index > len(self.file_list) - 1:
					self.file_index = len(self.file_list) - 1
				self.last_path = self.file_list[self.file_index][FILE_PATH]
				self.readFileList(self.current_path)
			else:
				print("MDC-I: FileOps: queryDeleteFileCallback: %s not a file" % afile[FILE_PATH])

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
