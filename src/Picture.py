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
from Movie import MDCMoviePlayer
from enigma import ePoint, eTimer, getDesktop, gPixmapPtr
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.StaticText import StaticText
from Components.config import config
from PictureUtils import rotatePictureExif, rotatePicture
from ConfigScreen import ConfigScreen
from globals import FILE_TYPE, FILE_PATH, FILE_MEDIA, FILE_META, TYPE_FILE
from skin import colorNames
from SkinUtils import getSkinPath
from FileInfo import FileInfo
from Slideshow import Slideshow
from Tools.LoadPixmap import LoadPixmap
from DelayedFunction import DelayedFunction
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.ScreenAnimations import ScreenAnimations


class MDCPictureSummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session, parent=parent)
		self.skinName = ["MDCSummary"]


class MDCPicturePlayer(Screen, HelpableScreen):

	def __init__(self, session, file_list, index, start_slideshow=False):
		print("MDC-I: Picture: MDCPicturePlayer: __init__")
		self.slideshow_active = False
		self.start_slideshow = start_slideshow
		self.external_slideshow = config.plugins.mediacockpit.animation.value in ["crossfade", "kenburns"]

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = ["MDCPicture"]

		self["actions"] = HelpableActionMap(
			self,
			"MDCActions",
			{
				"menu":		(self.showMenu,		_("Settings")),
				"info":		(self.showFileInfo,	_("Information")),
				"playpause":	(self.pause,		_("Pause/Resume") + " " + _("Slideshow")),
				"stop":		(self.stop,		_("Stop") + " " + _("Slideshow")),
				"historyNext":	(self.nextFile,		_("Next picture")),
				"right":	(self.nextFile,		_("Next picture")),
				"historyBack":	(self.prevFile,		_("Previous picture")),
				"left":		(self.prevFile,		_("Previous picture")),
				"yellow":	(self.rotateFile,	_("Rotate picture")),
				"blue":		(self.toggleInfo,	_("Toggle info")),
				"exit":		(self.exit,		_("Exit")),
				"red":		(self.exit,		_("Exit")),
			},
			prio=-1
		)

		self["picture_background"] = Label()
		self["picture"] = Pixmap()
		self["osd_info"] = Label()
		self["icon"] = Pixmap()
		self["icon"].hide()

		self["lcd_info"] = StaticText()
		self["lcd_title"] = StaticText()

		self.file_list = file_list
		self.file_index = index
		self.refresh_tiles = False
		self.direction = 1
		self.desktop_size = getDesktop(0).size()
		self.slideTimer = eTimer()
		self.slideTimer_conn = self.slideTimer.timeout.connect(self.nextSlide)

		screen_animations = ScreenAnimations()
		screen_animations.fromXML(resolveFilename(SCOPE_PLUGINS, "Extensions/MediaCockpit/animations.xml"))

		self.onLayoutFinish.append(self.LayoutFinish)

	def createSummary(self):
		return MDCPictureSummary

	def exit(self):
		config.plugins.mediacockpit.save()
		self.close(self.file_index, self.refresh_tiles)

	def LayoutFinish(self):
		#print("MDC: Picture: LayoutFinish")
		self.background_color = colorNames[config.plugins.mediacockpit.picture_background.value]
		self.foreground_color = colorNames[config.plugins.mediacockpit.picture_foreground.value]
		self.show_infoline = config.plugins.mediacockpit.show_picture_infobar.value
		self.slideshow_duration = config.plugins.mediacockpit.slideshow_duration.value * 1000

		self["picture"].instance.setShowHideAnimation(config.plugins.mediacockpit.animation.value)
		self["picture"].instance.invalidate()

		self["picture_background"].instance.setBackgroundColor(self.background_color)
		self["picture_background"].instance.invalidate()

		self["osd_info"].instance.setForegroundColor(self.foreground_color)
		self["osd_info"].instance.setBackgroundColor(self.background_color)
		self["osd_info"].instance.invalidate()

		if self.start_slideshow:
			self.start_slideshow = False
			DelayedFunction(100, self.pause)
		else:
			self.showFile()

	def updateOSDInfo(self):
		if self.show_infoline:
			if not self.slideshow_active:
				self["osd_info"].setText("(%d/%d) %s" % (self.file_index + 1, len(self.file_list), self.file_list[self.file_index][FILE_PATH]))
				self["osd_info"].show()
		else:
			self["osd_info"].hide()

		self.updateDisplayInfo()

	def updateDisplayInfo(self):
		direction = ""
		if self.slideshow_active:
			direction = "> " if self.direction > 0 else "< "
		self["lcd_title"].setText("%s%d/%d" % (direction, self.file_index + 1, len(self.file_list)))
		self["lcd_info"].setText(os.path.basename(self.file_list[self.file_index][FILE_PATH]))

	def nextSlide(self):
		#print("MDC: Picture: nextSlide")
		if self.direction > 0:
			self.nextFile()
		elif self.direction < 0:
			self.prevFile()

	def showFile(self):
		self.file = self.file_list[self.file_index]
		print("MDC-I: Picture: showFile: index: %s, file: %s" % (self.file_index, str(self.file)))
		self.updateOSDInfo()
		if self.file[FILE_MEDIA] == "picture":
			if self.external_slideshow and self.slideshow_active:
				self.session.openWithCallback(self.externalSlideshowCallback, Slideshow, self.file_list, self.file_index)
			else:
				self.showPicture(self.file[FILE_PATH])
		elif self.file[FILE_MEDIA] == "movie":
			self.showMovie()
		else:
			self.nextSlide()

	def showMovie(self):
		#print("MDC: Picture: showMovie: index: %s, file: %s" % (self.file_index, str(self.file)))
		self.slideTimer.stop()
		self["picture"].instance.setPixmap(gPixmapPtr())
		self.session.openWithCallback(self.showMovieCallback, MDCMoviePlayer, [self.file], 0, slideshow_active=self.slideshow_active)

	def showMovieCallback(self, slideshow_active=False):
		#print("MDC: Picture: showMovieCallback: slideshow_active: %s" % slideshow_active)
		self.slideshow_active = slideshow_active
		if self.slideshow_active:
			self["picture"].instance.setPixmap(gPixmapPtr())
			if not self.external_slideshow:
				self.slideTimer.start(self.slideshow_duration)
			self.nextSlide()
		else:
			self.showPicture(getSkinPath("images/" + "movie.svg"), icon=True)

	def showPicture(self, path, icon=False):
		#print("MDC: Picture: showPicture: show picture: path: %s, index: %s" % (path, self.file_index))
		self.updateOSDInfo()
		if icon:
			icon_size = self["icon"].instance.size()
			icon_pos = self["icon"].instance.position()
			self["picture"].instance.resize(icon_size)
			self["picture"].instance.move(icon_pos)
		else:
			meta_data = self.file_list[self.file_index][FILE_META]
			path = rotatePictureExif(path, meta_data)
			self["picture"].instance.setPixmap(gPixmapPtr())
			self["picture"].instance.resize(self.desktop_size)
			self["picture"].instance.move(ePoint(0, 0))
		picture = LoadPixmap(path=path, cached=False)
		self["picture"].instance.setPixmap(picture)

	def toggleInfo(self):
		self.show_infoline = not self.show_infoline
		self.updateOSDInfo()

	def rotateFile(self):
		if self.file_list[self.file_index][FILE_MEDIA] == "picture":
			tmpfile = rotatePicture(self.file_list[self.file_index][FILE_PATH], -90)
			picture = LoadPixmap(path=tmpfile, cached=False)
			self["picture"].instance.setPixmap(picture)
			self.refresh_tiles = True

	def nextFile(self):
		self.direction = 1
		self.file_index += 1
		if self.file_index > len(self.file_list) - 1:
			self.file_index = 0
		self.file = self.file_list[self.file_index]
		self.showFile()

	def prevFile(self):
		self.direction = -1
		self.file_index -= 1
		if self.file_index < 0:
			self.file_index = len(self.file_list) - 1
		self.file = self.file_list[self.file_index]
		self.showFile()

	def startSlideshow(self):
		self.slideshow_active = True
		self.slideTimer.start(self.slideshow_duration)
		self.updateOSDInfo()

	def stop(self):
		self.slideshow_active = False
		self.slideTimer.stop()
		self.updateOSDInfo()

	def pause(self):
		if not self.external_slideshow:
			if self.slideshow_active:
				self.stop()
			else:
				self.startSlideshow()
				self.nextSlide()
		else:
			self.slideshow_active = True
			self.showFile()

	def externalSlideshowCallback(self, file_index, slideshow_continue):
		self.file_index = file_index
		if slideshow_continue:
			self.nextSlide()
		else:
			self.exit()

	def showFileInfo(self):
		if not self.slideshow_active:
			if self.file_list[self.file_index][FILE_TYPE] == TYPE_FILE:
				self.session.openWithCallback(self.showFileInfoCallback, FileInfo, self.file_list, self.file_index)

	def showFileInfoCallback(self, _refresh_tiles, index):
		self.file_index = index
		self.LayoutFinish()

	def showMenu(self):
		if not self.slideshow_active:
			self.session.openWithCallback(self.showMenuCallback, ConfigScreen, "picture")

	def showMenuCallback(self, _reload=False):
		self.LayoutFinish()
