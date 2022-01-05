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


from .Debug import logger


def convertToUtf8(text, codepage="utf-8"):
	if text:
		try:
			text.decode(codepage)
		except UnicodeDecodeError:
			try:
				text = text.decode("cp1252")
			except UnicodeDecodeError:
				text = text.decode("iso-8859-1")
		if codepage != "utf-8":
			try:
				text = text.encode("utf-8")
			except UnicodeDecodeError as e:
				logger.error("exception: %s", e)
	return text.strip()
