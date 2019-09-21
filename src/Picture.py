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
from Components.config import config
from PictureUtils import rotatePicture, createThumbnail, setExifOrientation
from ConfigScreen import ConfigScreen
from globals import FILE_TYPE, FILE_PATH, FILE_MEDIA, TYPE_FILE, FILE_META
from skin import colorNames
from SkinUtils import getSkinPath
from MediaInfo import MediaInfo
from Slideshow import Slideshow
from Tools.LoadPixmap import LoadPixmap
from DelayTimer import DelayTimer
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.ScreenAnimations import ScreenAnimations
from MetaFile import MetaFile
from FileUtils import deleteFile
from Display import Display


class MDCPicturePlayer(Display, HelpableScreen, Screen, MetaFile):

	def __init__(self, session, file_list, file_index, start_slideshow=False, thumbnail_size=None):
		print("MDC-I: Picture: MDCPicturePlayer: __init__")
		self.session = session
		self.slideshow_active = False
		self.start_slideshow = start_slideshow
		self.thumbnail_size = thumbnail_size
		#print("MDC: Picture: __init__: file_index: %s, len(file_list): %s" % (file_index, len(file_list)))

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = "MDCPicture"
		Display.__init__(self)

		self["actions"] = HelpableActionMap(
			self,
			"MDCActions",
			{
				"menu":		(self.openMenu,		_("Settings")),
				"info":		(self.openInfo,		_("Information")),
				"playpause":	(self.playpause,	_("Pause/Resume") + " " + _("Slideshow")),
				"stop":		(self.stop,		_("Stop") + " " + _("Slideshow")),
				"keyNext":	(self.moveRight,	_("Next picture")),
				"right":	(self.moveRight,	_("Next picture")),
				"keyPrev":	(self.moveLeft,		_("Previous picture")),
				"left":		(self.moveLeft,		_("Previous picture")),
				"exit":		(self.exit,		_("Exit")),
				"red":		(self.red,		_("Exit")),
				"yellow":	(self.yellow,		_("Rotate picture")),
				"blue":		(self.blue,		_("Toggle info")),
			},
			prio=-1
		)

		self["picture_background"] = Label()
		self["picture"] = Pixmap()
		self["icon"] = Pixmap()
		self["icon"].hide()

		self.file_list = file_list
		self.file_index = file_index
		self.direction = 1
		self.desktop_size = getDesktop(0).size()
		self.slideTimer = eTimer()
		self.slideTimer_conn = self.slideTimer.timeout.connect(self.nextSlide)

		screen_animations = ScreenAnimations()
		screen_animations.fromXML(resolveFilename(SCOPE_PLUGINS, "Extensions/MediaCockpit/animations.xml"))

		#print("MDC: Picture: __init__: %s" % self.LayoutFinish)
		self.onLayoutFinish.append(self.LayoutFinish)
		#print("MDC: Picture: __init__: onLayoutFinish: %s" % str(self.onLayoutFinish))

	def LayoutFinish(self):
		print("MDC: Picture: LayoutFinish")
		self.background_color = colorNames[config.plugins.mediacockpit.picture_background.value]
		self.foreground_color = colorNames[config.plugins.mediacockpit.picture_foreground.value]
		self.show_infoline = config.plugins.mediacockpit.show_picture_infobar.value
		self.slideshow_duration = config.plugins.mediacockpit.slideshow_duration.value * 1000

		self.animation = config.plugins.mediacockpit.animation.value
		self.external_slideshow = int(self.animation) in range(-1, 11)
		if not self.external_slideshow:
			self["picture"].instance.setShowHideAnimation(self.animation)
		self["picture"].instance.invalidate()

		self["picture_background"].instance.setBackgroundColor(self.background_color)
		self["picture_background"].instance.invalidate()

		self["osd_info"].instance.setForegroundColor(self.foreground_color)
		self["osd_info"].instance.setBackgroundColor(self.background_color)
		self["osd_info"].instance.invalidate()

		if self.start_slideshow:
			self.start_slideshow = False
			DelayTimer(50, self.playpause)
		else:
			self.showFile()

	def showMediaInfo(self):
		show = self.show_infoline and not self.slideshow_active
		self.displayOSD(("(%d/%d) %s" % (self.file_index + 1, len(self.file_list), self.file_list[self.file_index][FILE_PATH])), show)
		direction = self.direction if self.slideshow_active else 0
		self.showMediaLCD(self.file_index + 1, len(self.file_list), self.file_list[self.file_index][FILE_PATH], direction)

	def nextSlide(self):
		#print("MDC: Picture: nextSlide")
		if self.direction > 0:
			self.moveRight()
		elif self.direction < 0:
			self.moveLeft()

	def showFile(self):
		print("MDC-I: Picture: showFile: file_index: %s, len(self.file_list): %s" % (self.file_index, len(self.file_list)))
		self.file = self.file_list[self.file_index]
		#print("MDC: Picture: showFile: index: %s, file: %s" % (self.file_index, str(self.file)))
		self.showMediaInfo()
		if self.file[FILE_MEDIA] == "picture":
			if self.external_slideshow and self.slideshow_active:
				self.session.openWithCallback(self.externalSlideshowCallback, Slideshow, self.file_list, self.file_index, self.animation)
			else:
				self.showPicture(self.file[FILE_PATH])
		elif self.file[FILE_MEDIA] == "movie":
			self.showMovie()
		else:
			self.nextSlide()

	def showMovie(self):
		#print("MDC: Picture: showMovie: index: %s, file: %s" % (self.file_index, str(self.file)))
		self["picture"].instance.setPixmap(gPixmapPtr())
		self.session.openWithCallback(self.showMovieCallback, MDCMoviePlayer, [self.file], 0, self.slideshow_active)

	def showMovieCallback(self, slideshow_active=False):
		#print("MDC: Picture: showMovieCallback: slideshow_active: %s" % slideshow_active)
		self.slideshow_active = slideshow_active
		if self.slideshow_active:
			self["picture"].instance.setPixmap(gPixmapPtr())
			self.nextSlide()
		else:
			self.showPicture(getSkinPath("images/" + "movie.svg"), icon=True)

	def showPicture(self, path, icon=False):
		print("MDC: Picture: showPicture: show picture: path: %s, index: %s" % (path, self.file_index))
		if icon:
			icon_size = self["icon"].instance.size()
			icon_pos = self["icon"].instance.position()
			self["picture"].instance.resize(icon_size)
			self["picture"].instance.move(icon_pos)
		else:
			filename, ext = os.path.splitext(path)
			path_transformed = filename + ".transformed" + ext
			if os.path.exists(path_transformed):
				path = path_transformed
			self["picture"].instance.setPixmap(gPixmapPtr())
			self["picture"].instance.resize(self.desktop_size)
			self["picture"].instance.move(ePoint(0, 0))
		picture = LoadPixmap(path, cached=False)
		self["picture"].instance.setPixmap(picture)
		if self.slideshow_active:
			self.slideTimer.start(self.slideshow_duration, True)
		self.showMediaInfo()

	def toggleInfo(self):
		self.show_infoline = not self.show_infoline
		self.showMediaInfo()

	def rotateFile(self):
		#print("MDC: Picture: rotateFile: file_index: %s" % self.file_index)
		x = self.file_list[self.file_index]
		if x[FILE_MEDIA] == "picture":
			path = x[FILE_PATH]
			filename, ext = os.path.splitext(path)
			out_file = in_file = filename + ".transformed" + ext
			if not os.path.exists(in_file):
				in_file = path
			rc = rotatePicture(in_file, out_file, 90)
			if rc:
				createThumbnail(path, (self.thumbnail_size.width(), self.thumbnail_size.height()), True)

				orientation = x[FILE_META]["Orientation"]
				if orientation == 1:
					new_orientation = 6
				elif orientation == 6:
					new_orientation = 3
				elif orientation == 3:
					new_orientation = 8
				elif orientation == 8:
					new_orientation = 1
					deleteFile(out_file)

				setExifOrientation(path, new_orientation)
				self.file_list[self.file_index][FILE_META]["Orientation"] = new_orientation
				self.saveMeta(path, self.file_list[self.file_index])
				if new_orientation == 1:
					deleteFile(out_file)

			self.showPicture(path)

### key functions

	def exit(self):
		self.slideshow_active = False
		config.plugins.mediacockpit.save()
		self.close(self.file_index)

	def red(self):
		self.exit()

	def green(self):
		pass

	def yellow(self):
		self.rotateFile()

	def blue(self):
		self.toggleInfo()

	def moveRight(self):
		self.direction = 1
		self.file_index += 1
		if self.file_index > len(self.file_list) - 1:
			self.file_index = 0
		self.file = self.file_list[self.file_index]
		self.showFile()

	def moveLeft(self):
		self.direction = -1
		self.file_index -= 1
		if self.file_index < 0:
			self.file_index = len(self.file_list) - 1
		self.file = self.file_list[self.file_index]
		self.showFile()

	def stop(self):
		self.slideshow_active = False
		self.showMediaInfo()

	def playpause(self):
		#print("MDC: Picture: playpause")
		if not self.external_slideshow:
			if self.slideshow_active:
				self.slideshow_active = False
				self.showMediaInfo()
			else:
				self.slideshow_active = True
				self.showFile()
		else:
			self.slideshow_active = True
			self.showFile()

	def externalSlideshowCallback(self, file_index, slideshow_continue, animation):
		self.file_index = file_index
		self.animation = animation
		if slideshow_continue:
			if file_index == 0:
				self.showFile()
			else:
				self.nextSlide()
		else:
			self.exit()

	def openInfo(self):
		if not self.slideshow_active:
			if self.file_list[self.file_index][FILE_TYPE] == TYPE_FILE:
				self.session.openWithCallback(self.openInfoCallback, MediaInfo, self.file_list, self.file_index)

	def openInfoCallback(self, index):
		self.file_index = index
		self.LayoutFinish()

	def openMenu(self):
		if not self.slideshow_active:
			self.session.openWithCallback(self.openMenuCallback, ConfigScreen, "picture")

	def openMenuCallback(self, _reload=False):
		self.LayoutFinish()
