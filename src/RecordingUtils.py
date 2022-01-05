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


from time import time
from RecordTimer import AFTEREVENT
import NavigationInstance
from Screens.InfoBar import InfoBar
try:
	from Plugins.SystemPlugins.SocketCockpit.SocketCockpit import SocketCockpit
except ImportError:
	class SocketCockpit():
		def __init__(self):
			return

		@staticmethod
		def getInstance():
			return None
from .Debug import logger


def getRecordings():
	logger.debug("...")
	recordings_list = []
	for timer in NavigationInstance.instance.RecordTimer.timer_list:
		if timer.isRunning() and not timer.justplay:
			recordings_list.append(timer.Filename)
	return recordings_list


def isRecording(path=""):
	timer = None
	for __timer in NavigationInstance.instance.RecordTimer.timer_list:
		if __timer.isRunning() and not __timer.justplay:
			if not path or path == __timer.Filename:
				timer = __timer
				break
	logger.debug("path: %s, is_recording: %s", path, timer is not None)
	return timer


def isRecordingOrRecordingSoon(session):
	logger.info("...")
	timer = isRecording()
	next_rec_time = session.nav.RecordTimer.getNextRecordingTime()
	return timer or (next_rec_time > 0 and (next_rec_time - time()) < 360)


def isTimeshifting():
	is_timeshifting = False
	if hasattr(InfoBar.instance, "isTimeshifting"):
		is_timeshifting = InfoBar.instance.isTimeshifting()
	logger.debug("is_timeshifting: %s", is_timeshifting)
	return is_timeshifting


def isFileStreaming():
	is_file_streaming = False
	socket_cockpit = SocketCockpit.getInstance()
	if socket_cockpit:
		is_file_streaming = socket_cockpit.isFileStreaming()
	logger.debug("is_file_streaming: %s", is_file_streaming)
	return is_file_streaming


def stopRecording(path):
	logger.info("path: %s", path)
	timer = isRecording(path)
	if timer:
		if timer.repeated:
			timer.enable()
			timer_afterEvent = timer.afterEvent
			timer.afterEvent = AFTEREVENT.NONE
			timer.processRepeated(findRunningEvent=False)
			NavigationInstance.instance.RecordTimer.doActivate(timer)
			timer.afterEvent = timer_afterEvent
			NavigationInstance.instance.RecordTimer.timeChanged(timer)
		else:
			timer.afterEvent = AFTEREVENT.NONE
			NavigationInstance.instance.RecordTimer.removeEntry(timer)
		logger.info("stopped path: %s", path)


def stopTimeshiftRecording():
	logger.info("...")
	if hasattr(InfoBar.instance, "stopTimeshiftRecording"):
		InfoBar.instance.stopTimeshiftRecording()


def startTimeshiftRecording():
	logger.info("...")
	if hasattr(InfoBar.instance, "startTimeshiftRecording"):
		InfoBar.instance.startTimeshiftRecording()
