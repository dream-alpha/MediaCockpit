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


import os
from __init__ import _
from Screens.Screen import Screen
from Screens.MessageBox import MessageBox
from Components.config import config
from Components.ActionMap import ActionMap
from Tools.BoundFunction import boundFunction
from Tools.LoadPixmap import LoadPixmap
from MetaFile import FILE_PATH, FILE_MEDIA
from enigma import eTimer
from Display import Display
from SkinUtils import getSkinPath
from ConfigInit import getAnimations
from KeyHelp import Help


MAX_SLIDES = 100


class SlideshowHelp(Help):
	def __init__(self, session):
		Help.__init__(self, session)

	def firstStart(self):
		alist = []
		alist.append((_("Exit"), LoadPixmap(getSkinPath("images/" + "key_red.png"), cached=False)))
		alist.append((_("Exit"), LoadPixmap(getSkinPath("images/" + "key_green.png"), cached=False)))
		alist.append(("", LoadPixmap(getSkinPath("images/" + "key_yellow.png"), cached=False)))
		alist.append((_("Toggle transition"), LoadPixmap(getSkinPath("images/" + "key_blue.png"), cached=False)))
		alist.append((_("Play/Pause"), LoadPixmap(getSkinPath("images/" + "key_playpause.png"), cached=False)))
		alist.append((_("Stop video/slideshow"), LoadPixmap(getSkinPath("images/" + "key_stop.png"), cached=False)))
		alist.append((_("Next slide"), LoadPixmap(getSkinPath("images/" + "key_next.png"), cached=False)))
		alist.append((_("Previous slide"), LoadPixmap(getSkinPath("images/" + "key_previous.png"), cached=False)))

		self["helplist"].setList(alist)
		self["helplist"].master.downstream_elements.setSelectionEnabled(0)


class MDCSlideshow(Display, Screen):

	def __init__(self, session, file_list, file_index, animation):
		print("MDC-I: Slideshow: __init__: file_index: %s, len(file_list): %s" % (file_index, len(file_list)))
		self.session = session
		self.file_list = file_list
		self.file_index = file_index
		self.animation = int(animation)
		self.direction = True
		Screen.__init__(self, session)
		self.skinName = [self.__class__.__name__]
		Display.__init__(self)

		self["actions"] = ActionMap(
			["MDCActions"],
			{
				"exit": self.exit,
				"stop": self.stop,
				"playpause": self.playpause,
				"left": self.left,
				"right": self.right,
				"blue": self.toggleTransitionMode,
				"help": self.help,
			},
			prio=-1
		)

		self.slide_path = ""
		self.slide_index = 0
		self.lastSlideTimer = eTimer()
		self.lastSlideTimer_conn = self.lastSlideTimer.timeout.connect(self.discontinue)
		self.slideshow_active = True
		self.slideshow_continue = config.plugins.mediacockpit.slideshow_loop.value
		self.slideshow_duration = config.plugins.mediacockpit.slideshow_duration.value * 1000
		self.animations = getAnimations()

		try:
			from Components.MerlinPictureViewerWidget import MerlinPictureViewer
			self["image"] = MerlinPictureViewer()
			self["image"].connectImageChanged(self.imageChanged)
			self.onLayoutFinish.append(self.startRun)
		except Exception:
			print("MDC-I: Slideshow: __init__: python-merlinpictureviewer package not installed")
			from Components.Pixmap import Pixmap
			self["image"] = Pixmap()
			self.onLayoutFinish.append(boundFunction(self.showMessageBox, _("Package") + " python-merlinpictureviewer " + _("is not installed")))

	def showMessageBox(self, msg):
		self.session.open(MessageBox, msg, MessageBox.TYPE_INFO)

	def startRun(self):
		#print("MDC: Slideshow: startRun")
		self.slide_list = []
		j = 0
		for i in range(self.file_index, len(self.file_list)):
			x = self.file_list[i]
			if x[FILE_MEDIA] == "picture":
				self.slide_list.append(x[FILE_PATH])
				j += 1
				if j >= MAX_SLIDES:
					self.slideshow_continue = True
					break
			else:
				self.slideshow_continue = True
				break

		if self.slide_list:
			self.slide_index = 0
			self.slide_path = self.slide_list[self.slide_index]
			self["image"].setTransitionMode(self.animation)
			self["image"].scaleToScreen(True)
			#print("MDC: Slideshow: startRun: start_index: %s, slide_list: %s" % (start_index, str(self.slide_list)))
			self["image"].startSlideShow(self.slide_list, self.slide_index, self.slideshow_duration, self.animation == "-1")
#			self.showLCDInfo()
		else:
			self.showMessageBox(_("No pictures to display"))

	def showLCDInfo(self):
		adir = os.path.basename(os.path.dirname(self.slide_path))
		direction = "> " if self.direction else "< "
		if not self.slideshow_active:
			direction = ""
		msg = "%s%d/%d" % (direction, self.file_index + self.slide_index + 1, len(self.file_list))
		print("MDC-I: Display: showLCDInfo: %s, slide_path: %s" % (msg, self.slide_path))
		self.displayLCD(msg, adir)

	def help(self):
		#print("MDC: Slideshow: help")
		self.session.open(SlideshowHelp)

	def exit(self):
		#print("MDC: Slideshow: exit")
		self.close(self.file_index + self.slide_index, True, False, False, self.direction, str(self.animation))

	def discontinue(self):
		#print("MDC: Slideshow: discontinue")
		self.close(self.file_index + self.slide_index, False, self.slideshow_active, self.slideshow_continue, self.direction, str(self.animation))

	def play(self):
		#print("MDC: Slideshow: play")
		self.slideshow_active = True
		self["image"].setState()
		self.showLCDInfo()

	def pause(self):
		#print("MDC: Slideshow: pause")
		self.slideshow_active = False
		self["image"].setState()
		self.showLCDInfo()

	def playpause(self):
		#print("MDC: Slideshow: playpause")
		if self.slideshow_active:
			self.pause()
		else:
			self.play()

	def stop(self):
		#print("MDC: Slideshow: stop")
		if self.slideshow_active:
			self.pause()

	def left(self):
		#print("MDC: Slideshow: left")
		self.direction = False
		self.slideshow_continue = True
		self.discontinue()

	def right(self):
		#print("MDC: Slideshow: right")
		self.direction = True
		self.slideshow_continue = True
		self.discontinue()

	def toggleTransitionMode(self):
		self.animation = (self.animation + 1) % 12
		#print("MDC: Slideshow: toggleTransitionMode: animation: %s" % self.animation)
		self["image"].setTransitionMode(self.animation)
		sanimation = "n/a"
		for animation in self.animations:
			if animation[0] == str(self.animation):
				sanimation = animation[1]
				break
		self.session.toastManager.showToast(_("Animation") + ": " + sanimation)

	def imageChanged(self):
		self.slide_path = self["image"].getCurrentFilename()
		self.slide_index = self["image"].getCurrentIndex()
		print("MDC-I: Slideshow: imageChanged: slide_index: %s, slide_path: %s, direction: %s" % (self.slide_index, self.slide_path, self.direction))
		if self.slide_index + 1 == len(self.slide_list):
			#print("MDC: Slideshow: imageChanged: last slide")
			self.lastSlideTimer.start(self.slideshow_duration, True)
		self.showLCDInfo()
