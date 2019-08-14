#!/usr/bin/python
# encoding: utf-8
#
# Copyright (C) 2011 betonme
# Copyright (C) 2018-2019 dream-alpha
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

from Components.Converter.ServicePosition import ServicePosition
from Components.Element import cached
import time


class MDCServicePosition(ServicePosition, object):
	def __init__(self, ptype):
		ServicePosition.__init__(self, ptype)

	@cached
	def getCutlist(self):
		service = self.source.service
		if service is not None:
			cut = service and service.cutList()
			return cut and cut.getCutList()
		return []

	cutlist = property(getCutlist)

	@cached
	def getLength(self):
		player = self.source.player
		return player.getLength()

	length = property(getLength)

	@cached
	def getPosition(self):
		player = self.source.player
		return player.getPosition()

	position = property(getPosition)

	@cached
	def getText(self):
		seek = self.getSeek()
		if seek is None:
			return ""
		else:
			if self.type == self.TYPE_LENGTH:
				l = self.length
			elif self.type == self.TYPE_POSITION:
				l = self.position
			elif self.type == self.TYPE_REMAINING:
				l = self.length - self.position
			elif self.type == self.TYPE_ENDTIME:
				l = (self.length - self.position) / 90000
				t = time.time()
				t = time.localtime(t + l)
				if self.showNoSeconds:
					return "%02d:%02d" % (t.tm_hour, t.tm_min)
				return "%02d:%02d:%02d" % (t.tm_hour, t.tm_min, t.tm_sec)

			if self.negate:
				l = -l

			if not self.detailed:
				l /= 90000
				if self.showHours:
					if self.showNoSeconds:
						return "%+d:%02d" % (l / 3600, l % 3600 / 60)
					return "%+d:%02d:%02d" % (l / 3600, l % 3600 / 60, l % 60)
				else:
					if self.showNoSeconds:
						return "%+d" % (l / 60)
					return "%+d:%02d" % (l / 60, l % 60)
			else:
				if self.showHours:
					return "%+d:%02d:%02d:%03d" % ((l / 3600 / 90000), (l / 90000) % 3600 / 60, (l / 90000) % 60, (l % 90000) / 90)
				return "%+d:%02d:%03d" % ((l / 60 / 90000), (l / 90000) % 60, (l % 90000) / 90)

	text = property(getText)
