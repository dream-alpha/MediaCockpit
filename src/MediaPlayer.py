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
from random import shuffle
from enigma import eTimer, getDesktop, gPixmapPtr
from Screens.HelpMenu import HelpableScreen
from Screens.Screen import Screen
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import config
from PictureUtils import rotatePicture, createThumbnail, setExifOrientation
from MetaFile import FILE_TYPE, FILE_PATH, FILE_MEDIA, TYPE_FILE, FILE_META
from skin import colorNames
from SkinUtils import getSkinPath
from MediaInfo import MediaInfo
from Slideshow import MDCSlideshow
from Tools.LoadPixmap import LoadPixmap
from DelayTimer import DelayTimer
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.ScreenAnimations import ScreenAnimations
from MetaFile import saveMeta
from FileUtils import deleteFile
from Display import Display
from ConsoleAppContainer import ConsoleAppContainer
from FileListUtils import previousIndex, nextIndex


class MDCMediaPlayer(Display, HelpableScreen, Screen):

	def __init__(self, session, file_list, file_index, start_slideshow=False, thumbnail_size=None, lastservice=None, song_list=None):
		print("MDC-I: MediaPlayer: MDCMediaPlayer: __init__: file_index: %s, start_slideshow: %s, file_list: %s, song_list: %s" % (file_index, start_slideshow, str(file_list), str(song_list)))
		self.session = session
		self.slideshow_active = False
		self.start_slideshow = start_slideshow
		self.thumbnail_size = thumbnail_size
		self.lastservice = lastservice

		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = "MDCMediaPlayer"
		Display.__init__(self)

		self["actions"] = HelpableActionMap(
			self,
			"MDCActions",
			{
				"info":		(self.openInfo,		_("Information")),
				"playpause":	(self.playpause,	_("Pause/Resume") + " " + _("Slideshow")),
				"stop":		(self.stop,		_("Stop video/slideshow")),
				"keyNext":	(self.right,		_("Next picture")),
				"right":	(self.right,		_("Next picture")),
				"keyPrev":	(self.left,		_("Previous picture")),
				"left":		(self.left,		_("Previous picture")),
				"exit":		(self.exit,		_("Exit")),
				"red":		(self.exit,		_("Exit")),
				"yellow":	(self.yellow,		_("Rotate picture")),
			},
			prio=-1
		)

		self["picture_background"] = Label()
		self["picture"] = Pixmap()

		self.file_list = file_list
		self.file_index = file_index
		self.song_list = song_list
		self.song_index = 0
		self.song_index_list = []
		self.direction = True
		self.desktop_size = getDesktop(0).size()
		self.slideTimer = eTimer()
		self.slideTimer_conn = self.slideTimer.timeout.connect(self.nextSlide)

		self.video_container = ConsoleAppContainer(self.showVideoCallback)
		self.audio_container = ConsoleAppContainer(self.playSongCallback)
		self.black_container = ConsoleAppContainer()

		screen_animations = ScreenAnimations()
		screen_animations.fromXML(resolveFilename(SCOPE_PLUGINS, "Extensions/MediaCockpit/animations.xml"))

		self.first_start = True
		self.onLayoutFinish.append(self.LayoutFinish)

	def LayoutFinish(self):
		#print("MDC: MediaPlayer: MDCMediaPlayer: LayoutFinish")
		if self.first_start:
			self.first_start = False
			if self.start_slideshow and self.song_list and self.file_list:
				self.song_index_list = range(len(self.song_list))
				shuffle(self.song_index_list)
				self.playSong(self.song_list[self.song_index_list[self.song_index]])
				#print("MDC: MediaPlayer: MDCMediaPlayer: LayoutFinish: song_index: %s, song_list: %s" % (self.song_index, str(self.song_list)))
		if self.file_list:
			self.background_color = colorNames[config.plugins.mediacockpit.picture_background.value]
			self.foreground_color = colorNames[config.plugins.mediacockpit.picture_foreground.value]
			self.slideshow_duration = config.plugins.mediacockpit.slideshow_duration.value * 1000

			self.animation = config.plugins.mediacockpit.animation.value
			self.external_slideshow = int(self.animation) in range(-1, 12) and self.direction
			print("MDC: MediaPlayer: MDCMediaPlayer LayoutFinish: animation: %s, external_slideshow: %s" % (self.animation, self.external_slideshow))
			if not self.external_slideshow:
				self["picture"].instance.setShowHideAnimation(self.animation)
			self["picture"].instance.invalidate()

			self["picture_background"].instance.setBackgroundColor(self.background_color)
			self["picture_background"].instance.invalidate()

			if self.start_slideshow:
				self.start_slideshow = False
				DelayTimer(50, self.playpause)
			else:
				self.showSlide()
		else:
			self.close(self.file_index)

	def showLCDInfo(self):
		#print("MDC-I: Display: showLCDInfo: file_index: %s, len(file_list): %s, slideshow_active: %s" % (self.file_index, len(self.file_list), self.slideshow_active))
		path = self.file_list[self.file_index][FILE_PATH]
		adir = os.path.basename(os.path.dirname(path))
		direction = "> " if self.direction else "< "
		if not self.slideshow_active:
			direction = ""
		self.displayLCD("%s%d/%d" % (direction, self.file_index + 1, len(self.file_list)), adir)

### slide functions

	def nextSlide(self):
		print("MDC: MediaPlayer: MDCMediaPlayer: nextSlide")
		self.slideTimer.stop()
		self.stopVideo()
		if self.direction:
			self.file_index = nextIndex(self.file_index, len(self.file_list))
		else:
			self.file_index = previousIndex(self.file_index, len(self.file_list))
		self.showSlide()

	def showSlide(self):
		print("MDC-I: MediaPlayer: MDCMediaPlayer: showSlide: file_index: %s, len(self.file_list): %s" % (self.file_index, len(self.file_list)))
		self.external_slideshow = int(self.animation) in range(-1, 12) and self.direction
		self.file = self.file_list[self.file_index]
		if self.file[FILE_MEDIA] == "picture":
			if self.slideshow_active and self.external_slideshow:
				self.externalSlideshow()
			else:
				self.show()
				self.showPicture(self.file[FILE_PATH])
				if self.slideshow_active:
					self.slideTimer.start(self.slideshow_duration, True)
			self.showLCDInfo()
		elif self.file[FILE_MEDIA] == "movie":
			self.hide()
			self.showVideo(self.file[FILE_PATH])
		else:
			self.nextSlide()

### picuture functions

	def showPicture(self, path):
		#print("MDC: MediaPlayer: MDCMediaPlayer: showPicture: show picture: path: %s, index: %s" % (path, self.file_index))
		filename, ext = os.path.splitext(path)
		path_transformed = filename + ".transformed" + ext
		path = path_transformed if os.path.exists(path_transformed) else path
		self["picture"].instance.setPixmap(gPixmapPtr())
		picture = LoadPixmap(path, cached=False)
		self["picture"].instance.setPixmap(picture)

	def rotatePicture(self):
		#print("MDC: MediaPlayer: MDCMediaPlayer: rotatePicture: file_index: %s" % self.file_index)
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
				saveMeta(path, self.file_list[self.file_index])
				if new_orientation == 1:
					deleteFile(out_file)

			self.showPicture(path)

### video functions

	def showVideo(self, filename):
		print("MDC-I: MediaPlayer: MDCMediaPlayer: showVideo: filename: %s" % filename)
		self["picture"].instance.setPixmap(gPixmapPtr())
		cmd = "gst-launch-1.0 playbin -v uri='file://%s'" % filename
		if self.song_list:
			cmd += ' flags=0x51'
		#print("MDC: MediaPlayer: MDCMediaPlayer: showVideo: cmd: %s" % cmd)
		self.video_container.execute(cmd)
		self.showLCDInfo()

	def showVideoCallback(self):
		print("MDC: MediaPlayer: MDCMediaPlayer: showVideoCallback: slideshow_active: %s" % self.slideshow_active)
		if self.slideshow_active:
			self.nextSlide()

	def stopVideo(self):
		print("MDC: MediaPlayer: stopVideo: media: %s" % self.file_list[self.file_index][FILE_MEDIA])
		if self.file_list[self.file_index][FILE_MEDIA] == "movie":
			self.video_container.kill()
			if self.slideshow_active:
				self.blackScreen()

	def blackScreen(self):
		filename = getSkinPath("images/black.mvi")
		cmd = "showiframe %s" % filename
		#print("MDC: MediaPlayer: MDCMediaPlayer: blackScreen: cmd: %s" % cmd)
		self.black_container.execute(cmd)

### external slideshow functions

	def externalSlideshow(self):
		self.session.openWithCallback(self.externalSlideshowCallback, MDCSlideshow, self.file_list, self.file_index, self.animation)

	def externalSlideshowCallback(self, file_index, slideshow_exit, slideshow_active, slideshow_continue, direction, animation):
		print("MDC-I: MediaPlayer: externalSlideShowCallback: file_index: %s, slideshow_active: %s, slideshow_continue: %s, direction: %s" % (file_index, slideshow_active, slideshow_continue, direction))
		self.file_index = file_index
		self.slideshow_active = slideshow_active and slideshow_continue
		self.direction = direction
		self.animation = animation
		if not slideshow_exit:
			if slideshow_continue:
				self.nextSlide()
			else:
				self.showSlide()
		else:
			self.exit()

### song functions

	def playSong(self, x):
		print("MDC-I: MediaPlayer: MDCMediaPlayer: playSong: song_index: %s, x: %s" % (self.song_index, str(x)))
		cmd = "gst-launch-1.0 playbin uri='file://%s' audio-sink='alsasink'" % x[FILE_PATH]
		#print("MDC: MediaPlayer: MDCMediaPlayer: playSong: cmd: %s" % cmd)
		self.audio_container.execute(cmd)

	def playSongCallback(self):
		#print("MDC: MediaPlayer: MDCMediaPlayer: playSongCallback")
		self.song_index = (self.song_index + 1) % len(self.song_list)
		self.playSong(self.song_list[self.song_index_list[self.song_index]])

	def stopSong(self):
		self.audio_container.kill()

### key functions

	def exit(self):
		self.stopVideo()
		self.stopSong()
		config.plugins.mediacockpit.animation.value = self.animation
		config.plugins.mediacockpit.animation.save()
		path = self.file_list[self.file_index][FILE_PATH]
		#print("MDC: MediaPlayer: MDCMediaPlayer: exit: file_index: %s, path: %s" % (self.file_index, path))
		self.close(path)

	def yellow(self):
		self.session.toastManager.showToast(_("Rotating picture..."))
		self.rotatePicture()

	def right(self):
		self.direction = True
		self.nextSlide()

	def left(self):
		self.direction = False
		self.nextSlide()

	def stop(self):
		if self.file_list[self.file_index][FILE_MEDIA] == "movie":
			self.stopVideo()
			DelayTimer(250, self.showVideoCallback)
		else:
			self.slideshow_active = False
			self.slideTimer.stop()
			self.showLCDInfo()

	def playpause(self):
		#print("MDC: MediaPlayer: MDCMediaPlayer: playpause")
		self.slideshow_active = not self.slideshow_active
		if self.slideshow_active:
			self.nextSlide()
		else:
			self.slideTimer.stop()
			self.video_container.kill()
			self.showLCDInfo()

	def openInfo(self):
		if not self.slideshow_active and self.file_list[self.file_index][FILE_TYPE] == TYPE_FILE:
			self.session.openWithCallback(self.openInfoCallback, MediaInfo, self.file_list, self.file_index)

	def openInfoCallback(self, file_index):
		self.file_index = file_index
		self.LayoutFinish()
