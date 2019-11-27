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


from MetaFile import FILE_PATH


def nextIndex(file_index, file_list_length):
	return (file_index + 1) % file_list_length


def previousIndex(file_index, file_list_length):
	return file_index - 1 if file_index else file_list_length - 1


def getIndex(file_list, path):
	file_index = 0 if file_list else -1
	for i, x in enumerate(file_list):
		if x[FILE_PATH] == path:
			file_index = i
			break
	return file_index
