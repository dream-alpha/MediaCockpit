#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2019 by dream-alpha
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


from __init__ import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.config import config
from Components.ActionMap import ActionMap
from globals import FILE_PATH, FILE_MEDIA
from enigma import eTimer
from Display import Display


MAX_SLIDES = 100


class Slideshow(Display, Screen, object):

	def __init__(self, session, file_list, file_index, animation):
		print("MDC-I: Slideshow: __init__: file_index: %s" % file_index)
		self.session = session
		self.file_list = file_list
		self.file_index = file_index
		self.animation = int(animation)
		self.direction = 0
		Screen.__init__(self, session)
		self.skinName = "MDCSlideshow"
		Display.__init__(self)

		self["actions"] = ActionMap(
			["MDCActions"],
			{
				"exit": self.exit,
				"playpause": self.playpause,
				"stop":	self.stop,
				"left": self.left,
				"right": self.right,
				"blue": self.blue,
			},
			prio=-1
		)

		self.slide_path = ""
		self.slide_index = 0
		self.slides = 0
		self.lastSlideTimer = eTimer()
		self.lastSlideTimer_conn = self.lastSlideTimer.timeout.connect(self.leave)
		self.slideshow_active = True
		self.slideshow_continue = False
		self.request_to_leave = False

		try:
			from Components.MerlinPictureViewerWidget import MerlinPictureViewer
			self["image"] = MerlinPictureViewer()
			self["image"].connectImageChanged(self.imageChanged)
			self.onFirstExecBegin.append(self.startRun)
		except Exception:
			print("MDC-I: Slideshow: __init__: python-merlinpictureviewer package not installed")
			from Components.Pixmap import Pixmap
			self["image"] = Pixmap()
			self.onFirstExecBegin.append(self.showMessageBox)

	def showMessageBox(self):
		self.session.open(MessageBox, _("Package") + " python-merlinpictureviewer " + _("is not installed"), MessageBox.TYPE_ERROR)

	def startRun(self):
		self.slideshow_duration = config.plugins.mediacockpit.slideshow_duration.value * 1000
		self.alist = []
		start_index = 0
		j = 0
		for i in range(self.file_index, len(self.file_list)):
			x = self.file_list[i]
			if x[FILE_MEDIA] == "picture":
				self.alist.append(x[FILE_PATH])
				j += 1
				if j >= MAX_SLIDES:
					self.slideshow_continue = True
					break
			else:
				self.slideshow_continue = True
				break

		self.slides = len(self.alist)
		self.slide_index = 0
		self.slide_path = self.alist[start_index]

		self["image"].setTransitionMode(self.animation)
		self["image"].scaleToScreen(True)
		self["image"].startSlideShow(self.alist, start_index, self.slideshow_duration, self.animation == "-1")
		self.play()

	def showDisplayInfo(self):
		direction = 1 if self.slideshow_active else 0
		self.showMediaLCD(self.file_index + self.slide_index + 1, len(self.file_list), self.slide_path, direction)

	def exit(self):
		self.slideshow_active = False
		self.leave()

	def leave(self):
		slideshow_continue = (
			self.slideshow_active and (
				self.slideshow_continue
				or self.file_index + self.slide_index + 1 != len(self.file_list)
				or config.plugins.mediacockpit.slideshow_loop.value
			)
		)
		#print("MDC: Slideshow: leave: file_index: %s, slide_index: %s, len(file_list): %s" % (self.file_index, self.slide_index, len(self.file_list)))
		if slideshow_continue and self.file_index + self.slide_index + 1 == len(self.file_list):
			continue_index = 0
		else:
			continue_index = self.file_index + self.slide_index
		self.close(continue_index, slideshow_continue, str(self.animation))

	def play(self):
		self.slideshow_active = True
		self.direction = 1

	def stop(self):
		self.slideshow_active = False
		self.direction = 0
		self.showDisplayInfo()

	def playpause(self):
		self["image"].setState()
		if self.slideshow_active:
			self.stop()
		else:
			self.play()

	def left(self):
		self.slideshow_active = False
		self.direction = -1
		self["image"].skipImage(self.direction)

	def right(self):
		self.slideshow_active = False
		self.direction = 1
		self["image"].skipImage(self.direction)

	def blue(self):
		self.toggleTransitionMode()

	def toggleTransitionMode(self):
		self.animation = self.animation + 1 if self.animation < 11 else 0
		#print("MDC: Slideshow: toggleTransitionMode: animation: %s" % self.animation)
		self["image"].setTransitionMode(self.animation)

	def imageChanged(self):
		print("MDC-I: Slideshow: imageChanged: direction: %s" % self.direction)
		if self.slideshow_active:
			path = self["image"].getCurrentFilename()
			if self.slide_path != path or len(self.alist) == 1:
				self.slide_index = (self.slide_index + 1) % self.slides
				self.slide_path = path
				if self.slide_index + 1 == self.slides:
					#print("MDC: Slideshow: nextSlide: request_to_leave, timer: %s" % self.slideshow_duration)
					self.request_to_leave = True
					self.lastSlideTimer.start(self.slideshow_duration, True)
		else:
			if self.direction == 1:
				self.slide_index += 1
				if self.slide_index > self.slides - 1:
					self.slide_index = 0
			elif self.direction == -1:
				self.slide_index -= 1
				if self.slide_index < 0:
					self.slide_index = 0
		self.showDisplayInfo()
