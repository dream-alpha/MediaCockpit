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


import os
from __init__ import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Tools.BoundFunction import boundFunction
from Components.config import config
from Components.ActionMap import ActionMap
from Components.Sources.StaticText import StaticText
from globals import FILE_PATH, FILE_MEDIA, FILE_META
from PictureUtils import rotatePictureExif, scalePicture
from enigma import eTimer, getDesktop


MAX_SLIDES = 100
POLL_TIMEOUT = 250


class MDCSlideshowSummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self.skinName = ["MDCSummary"]


class Slideshow(Screen):

	def __init__(self, session, file_list, file_index):
		#print("MDC: Slideshow: __init__: file_index: %s" % file_index)
		self.session = session
		self.file_list = file_list
		self.file_index = file_index
		Screen.__init__(self, session)
		self.skinName = ["MDCSlideshow"]
		self["actions"] = ActionMap(
			["MDCActions"],
			{
				"exit": self.exit,
				"right": boundFunction(self.scrollX, -1),
				"left": boundFunction(self.scrollX, 1),
				"up": boundFunction(self.scrollY, 1),
				"down": boundFunction(self.scrollY, -1),
				"playpause": self.pause,
				"stop":	self.exit,
				"seekBack": boundFunction(self.skipPicture, -1),
				"seekFwd": boundFunction(self.skipPicture, 1),
				"nextBouquet": boundFunction(self.setZoom, 1),
				"prevBouquet": boundFunction(self.setZoom, -1),
			},
			-1
		)

		self.slide_path = ""
		self.slide_index = 0
		self.slides = 0
		self.slideCounterTimer = eTimer()
		self.slideCounterTimer_conn = self.slideCounterTimer.timeout.connect(self.nextSlide)
		self.slideshow_active = True
		self.slideshow_continue = False
		self.request_to_leave = False

		self["lcd_info"] = StaticText()
		self["lcd_title"] = StaticText()

		try:
			from Components.MerlinMusicPlayerWidget import MerlinImageDisplay
			self["image"] = MerlinImageDisplay()
			self.onFirstExecBegin.append(self.startRun)
		except Exception:
			print("MDC-I: Slideshow: __init__: merlin musicplayer2 plugin not installed")
			self.onFirstExecBegin.append(self.showMessageBox)

	def createSummary(self):
		return MDCSlideshowSummary

	def showMessageBox(self):
		self.session.open(MessageBox, _("Package python-merlinmusicplayer is not installed"), MessageBox.TYPE_ERROR)

	def startRun(self):
		self.slideshow_duration = config.plugins.mediacockpit.slideshow_duration.value * 1000
		self.alist = []
		start_index = 0
		j = 0
		for i in range(self.file_index, len(self.file_list)):
			x = self.file_list[i]
			if x[FILE_MEDIA] == "picture":
				path = x[FILE_PATH]
				path = rotatePictureExif(path, x[FILE_META])
				desktop_size = getDesktop(0).size()
				path = scalePicture(path, (desktop_size.width(), desktop_size.height()))
				self.alist.append(path)
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
		self["image"].startSlideShow(self.alist, start_index, self.slideshow_duration, config.plugins.mediacockpit.animation.value == "kenburns")
		self.nextSlide()

	def nextSlide(self):
		#print("MDC: Slideshow: nextSlide: self.slide_index: %s, self.slides: %s, request_to_leave: %s" % (self.slide_index, self.slides, self.request_to_leave))
		if self.request_to_leave:
			self.slideCounterTimer.stop()
			self.leave()
		else:
			if self.slideshow_active:
				path = self["image"].getCurrentFilename()
				if self.slide_path != path or len(self.alist) == 1:
					self.slide_index = (self.slide_index + 1) % self.slides
					self.slide_path = path
					if self.slide_index + 1 == self.slides:
						#print("MDC: Slideshow: nextSlide: request_to_leave, timer: %s" % self.slideshow_duration)
						self.request_to_leave = True
						self.slideCounterTimer.start(self.slideshow_duration, True)
				if not self.request_to_leave:
					self.slideCounterTimer.start(POLL_TIMEOUT, True)

			self.updateDisplayInfo()

	def updateDisplayInfo(self):
		direction = ""
		if self.slideshow_active:
			direction = "> "
		self["lcd_title"].setText("%s%d/%d" % (direction, self.file_index + self.slide_index + 1, len(self.file_list)))
		slide_dir = os.path.dirname(self.slide_path)
		self["lcd_info"].setText(os.path.basename(slide_dir))

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
		self.close(self.file_index + self.slide_index, slideshow_continue)

	def pause(self):
		self["image"].setState()
		self.slideshow_active = not self.slideshow_active
		if self.slideshow_active:
			self.nextSlide()

	def skipPicture(self, direction):
		self.slideshow_active = False
		self["image"].skipImage(direction)
		if direction == 1:
			self.slide_index += 1
			if self.slide_index > self.slides - 1:
				self.slide_index = 0
		else:
			self.slide_index -= 1
			if self.slide_index < 0:
				self.slide_index = 0
		self.updateDisplayInfo()

	def setZoom(self, direction):
		self.slideshow_active = False
		self["image"].setZoom(direction)

	def scrollY(self, direction):
		self.slideshow_active = False
		self["image"].setScrollY(direction)

	def scrollX(self, direction):
		self.slideshow_active = False
		if self["image"].isZoomMode():
			self["image"].setScrollX(direction)
		else:
			self.skipPicture(direction * -1)
