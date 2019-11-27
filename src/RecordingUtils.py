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
from enigma import eServiceReference
from Components.config import config
from RecordTimer import AFTEREVENT
import NavigationInstance
from ServiceUtils import sidDVB


def isRecording(path):
	#print("MVC: RecordingUtils: isRecording: path: %s" % path)
	timer = None
	if path:
		for __timer in NavigationInstance.instance.RecordTimer.timer_list:
			if __timer.isRunning() and not __timer.justplay and path == __timer.Filename:
				timer = __timer
				break
	return timer


def stopRecording(path):
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
		print("MVC-I: RecordingUtils: stopRecording: path: %s" % path)


def isCutting(path):
	#print("MVC: RecordingUtils: isCutting: path: %s" % path)
	filename, _ext = os.path.splitext(path)
	return filename.endswith("_") and not os.path.exists(filename + ".eit")


def getRecording(path, include_margin_before=True):
#	import datetime
	recording = None
	timer = isRecording(path)
	if timer:
		#print("MVC: RecordingUtils: getRecording: path: %s" % path)
		#print("MVC: RecordingUtils: getRecording: include_margin_before: %s" % include_margin_before)
		if include_margin_before:
			from ServiceCenter import ServiceCenter
			service = eServiceReference(sidDVB, 0, path)
			#print("MVC: RecordingUtils: getRecording: service path: " + service.getPath())
			recording_start = ServiceCenter.getInstance().info(service).getStartTime()
#			#print("MVC: RecordingUtils: getRecording: recording_start: " + str(datetime.datetime.fromtimestamp(recording_start)))
			delta = recording_start - timer.begin
			if delta > config.recording.margin_before.value * 60:
				#print("MVC: RecordingUtils: getRecording: late recording")
				rec_start = recording_start
			elif delta > 0:
				#print("MVC: RecordingUtils: getRecording: late recording but within margin_before")
				rec_start = recording_start - (config.recording.margin_before.value - delta)
			else:
				#print("MVC: RecordingUtils: getRecording: ontime recording")
				rec_start = timer.begin
		else:
			recording_start = int(os.stat(path).st_ctime)  # timestamp from file
#			#print("MVC: RecordingUtils: getRecording: recording_start: " + str(datetime.datetime.fromtimestamp(recording_start)))
			delta = recording_start - timer.begin
			if delta > config.recording.margin_before.value * 60:
				#print("MVC: RecordingUtils: getRecording: late recording")
				rec_start = recording_start
			else:
				#print("MVC: RecordingUtils: getRecording: ontime recording or within margin_before")
				rec_start = timer.begin + config.recording.margin_before.value * 60
		rec_end = timer.end - config.recording.margin_after.value * 60
		recording = (rec_start, rec_end, timer.service_ref.ref)
	return recording
