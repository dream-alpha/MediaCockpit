#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2020 by dream-alpha
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


from operator import isCallable
from enigma import eTimer


timers = []


class DelayTimer():

	def __init__(self, delay, function, *params):
		#print("MDC: DelayTimer: __init__: delay: %s" % delay)
		if isCallable(function):
			timers.append(self)
			self.delay = delay  # in milliseconds
			self.function = function
			self.params = params
			self.timer = eTimer()
			self.timer_conn = self.timer.timeout.connect(self.__fire)
			if self.delay:
				self.__start()
			else:
				self.__fire()

	def __fire(self):
		#print("MDC: DelayTimer: __fire")
		timers.remove(self)
		self.function(*self.params)

	def __start(self):
		self.timer.start(self.delay, True)
