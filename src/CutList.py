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
from RecordingUtils import isRecording
from CutListUtils import packCutList, unpackCutList, replaceLast, replaceLength, removeMarks, mergeCutList, backupCutsFile
from FileUtils import readFile, writeFile, deleteFile

# http://git.opendreambox.org/?p=enigma2.git;a=blob;f=doc/FILEFORMAT

# cut_list data structure
# cut_list[x][0] = pts  = long long
# cut_list[x][1] = what = long


def updateFromCuesheet(path):
	#print("MVC: CutList: updateFromCuesheet")
	backup_cut_file = path + ".cuts.save"
	if os.path.exists(backup_cut_file):
		#print("MVC: CutListUtils: mergeBackupCutsFile: reading from Backup-File")
		cut_list = __getCutFile(path)
		data = readFile(backup_cut_file)
		backup_cut_list = unpackCutList(data)
		#print("MVC: CutList: updateFromCuesheet: backup_cut_list: %s" % backup_cut_list)
		cut_list = mergeCutList(cut_list, backup_cut_list)
		writeFile(path + ".cuts", packCutList(cut_list))
		deleteFile(backup_cut_file)
		__putCutFile(path, cut_list)
	else:
		#print("MVC: CutList: updateFromCuesheet: no Backup-File found: %s" % backup_cut_file)
		pass


def writeCutList(path, cut_list):
	#print("MVC: CutList: setCutList: " + str(cut_list))
	__putCutFile(path, cut_list)


def fetchCutList(path):
	return __getCutFile(path)


def resetLastCutList(path):
	#print("MVC: resetLastCutList: path: %s" % path)
	cut_list = replaceLast(__getCutFile(path), 0)
	#print("MVC: resetLastCutList: cut_list: %s" % cut_list)
	__putCutFile(path, cut_list)


def updateCutList(path, play, length):
	#print("MVC: CutList: updateCutList: play: " + str(play) + ", length: " + str(length))
	cut_list = replaceLast(__getCutFile(path), play)
	cut_list = replaceLength(cut_list, length)
	__putCutFile(path, cut_list)


def removeMarksCutList(path):
	cut_list = removeMarks(__getCutFile(path))
	__putCutFile(path, cut_list)


def deleteFileCutList(path):
	data = ""
	try:
		from FileCache import FileCache
		FileCache.getInstance().update(path, pcuts=data)
	except Exception:
		pass
	deleteFile(path)


def reloadCutListFromFile(path):
	cut_list = []
	data = readFile(path + ".cuts")
	try:
		from FileCache import FileCache
		FileCache.getInstance().update(path, pcuts=data)
	except Exception:
		pass
	cut_list = unpackCutList(data)
	return cut_list


def __getCutFile(path):
	cut_list = []
	if path:
		try:
			from FileCache import FileCache, FILE_IDX_CUTS
			#print("MVC: CutList: __getCutFile: reading cut_list from cache: %s" % path)
			filedata = FileCache.getInstance().getFile(path)
			data = filedata[FILE_IDX_CUTS]
		except Exception:
			data = readFile(path + ".cuts")
		cut_list = unpackCutList(data)
	#print("MVC: CutList: __getCutFile: cut_list: " + str(cut_list))
	return cut_list


def __putCutFile(path, cut_list):
	if path:
		#print("MVC: CutList: __putCutFile: %s, cut_list: %s" % (path, cut_list))
		data = packCutList(cut_list)
		writeFile(path + ".cuts", data)

		# update file in cache
		try:
			from FileCache import FileCache
			#print("MVC: CutList: __putCutFile: updating cut_list in cache: %s" % path)
			FileCache.getInstance().update(path, pcuts=data)
		except Exception:
			pass

		# always backup cutlist when recording, it will be merged with enigma-cutfile after recording
		ts_path, __ = os.path.splitext(path)
		if isRecording(ts_path):
			#print("MVC: CutList: __putCutFile: creating backup file: " + path)
			backupCutsFile(ts_path)
