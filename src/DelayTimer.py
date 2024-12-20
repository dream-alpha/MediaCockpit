#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
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


from enigma import eTimer


timer_instances = []


class DelayTimer():

	def __init__(self, delay, function, *args):
		if delay:
			timer_instances.append(self)
			self.timer = eTimer()
			self.function = function
			self.args = args
			self.timer_conn = self.timer.timeout.connect(self.fire)
			self.timer.start(delay, True)
		else:
			function(*args)

	def fire(self):
		timer_instances.remove(self)
		self.function(*self.args)

	def stop(self):
		if self in timer_instances:
			timer_instances.remove(self)
			self.timer.stop()

	@staticmethod
	def stopAll():
		for timer_instance in timer_instances:
			timer_instance.timer.stop()
