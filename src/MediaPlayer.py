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
from PictureUtils import getPicturePath, rotatePicture, createThumbnail, setExifOrientation
from MetaFile import FILE_TYPE, FILE_PATH, FILE_MEDIA, TYPE_FILE, FILE_META
from skin import colorNames
from SkinUtils import getSkinPath
from MediaInfo import MediaInfo
from Tools.LoadPixmap import LoadPixmap
from DelayTimer import DelayTimer
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Components.ScreenAnimations import ScreenAnimations
from MetaFile import saveMeta
from FileUtils import deleteFile
from Display import Display
from ConsoleAppContainer import ConsoleAppContainer
from FileListUtils import previousIndex, nextIndex
from ConfigInit import int_slideshow_animations, ext_slideshow_animations


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
		self.skinName = self.__class__.__name__
		Display.__init__(self)

		self["actions"] = HelpableActionMap(
			self,
			"MDCActions",
			{
				"info":		(self.openInfo,			_("Information")),
				"playpause":	(self.playpause,		_("Play/Pause") + " " + _("Slideshow")),
				"stop":		(self.stop,			_("Stop video/slideshow")),
				"keyNext":	(self.right,			_("Next picture")),
				"right":	(self.right,			_("Next picture")),
				"keyPrev":	(self.left,			_("Previous picture")),
				"left":		(self.left,			_("Previous picture")),
				"exit":		(self.exit,			_("Exit")),
				"red":		(self.exit,			_("Exit")),
				"yellow":	(self.yellow,			_("Rotate picture")),
				"blue": 	(self.toggleTransitionMode,	_("Toggle transition")),
			},
			prio=-1
		)

		self["picture_background"] = Label()
		self["picture"] = Pixmap()
		self["image"] = Pixmap()
		self.slideshow_animations = int_slideshow_animations
		self.animation = int(int_slideshow_animations[0][0])
		self.external_slideshow = False
		try:
			from Components.MerlinPictureViewerWidget import MerlinPictureViewer
			self["image"] = MerlinPictureViewer()
			self["image"].connectImageChanged(self.imageChanged)
			self.slideshow_animations = ext_slideshow_animations
			self.animation = int(ext_slideshow_animations[0][0])
			self.external_slideshow = True
		except Exception:
			print("MDC-I: MediaPlayer: __init__: python-merlinpictureviewer package not installed")

		self.file_list = file_list
		self.file_index = file_index
		self.file = None
		self.song_list = song_list if song_list is not None else []
		self.song_index = 0
		self.song_index_list = range(len(self.song_list))
		self.direction = True
		self.desktop_size = getDesktop(0).size()
		self.slideTimer = eTimer()
		self.slideTimer_conn = self.slideTimer.timeout.connect(self.nextSlide)

		self.video_container = ConsoleAppContainer(self.showVideoCallback)
		self.audio_container = ConsoleAppContainer(self.playSongCallback)
		self.black_container = ConsoleAppContainer()

		screen_animations = ScreenAnimations()
		screen_animations.fromXML(resolveFilename(SCOPE_PLUGINS, "Extensions/MediaCockpit/animations.xml"))

		for animation in self.slideshow_animations:
			if animation[0] == config.plugins.mediacockpit.animation.value:
				self.animation = int(animation[0])
				break
		#print("MDC: MediaPlayer: MDCMediaPlayer __init__: animation: %s" % self.animation)

		self.toast = None
		self.onLayoutFinish.append(self.LayoutFinish)

	def LayoutFinish(self):
		#print("MDC: MediaPlayer: MDCMediaPlayer: LayoutFinish")
		self.file = self.file_list[self.file_index]
		if self.file_list:
			self.background_color = colorNames[config.plugins.mediacockpit.picture_background.value]
			self.foreground_color = colorNames[config.plugins.mediacockpit.picture_foreground.value]
			self["picture_background"].instance.setBackgroundColor(self.background_color)
			self["picture_background"].instance.invalidate()
			self.slideshow_duration = config.plugins.mediacockpit.slideshow_duration.value * 1000
			if self.external_slideshow:
				self["image"].scaleToScreen(True)
			self.setSlideshowAnimation(self.animation)
			if self.start_slideshow:
				self.start_slideshow = False
				if self.song_list:
					shuffle(self.song_index_list)
					self.playSong(self.song_list[self.song_index_list[self.song_index]])
					#print("MDC: MediaPlayer: MDCMediaPlayer: LayoutFinish: song_index: %s, song_list: %s" % (self.song_index, str(self.song_list)))
				self.playpause()
			else:
				self.showSlide()
		else:
			self.close(self.file_index)

	def setSlideshowAnimation(self, animation):
		#print("MDC: MediaPlayer: setSlideshowAnimation: animation: %s" % animation)
		for slideshow_animation in self.slideshow_animations:
			if slideshow_animation[0] == str(animation):
				if self.external_slideshow:
					#print("MDC: MediaPlayer: setSlideshowAnimation: external: %s" % str(animation))
					self["image"].setTransitionMode(animation)
				else:
					#print("MDC: MediaPlayer: setSlideshowAnimation: internal: %s" % str(animation))
					self["picture"].instance.setShowHideAnimation(str(animation))
					self["picture"].instance.invalidate()
				break

	def showLCDInfo(self):
		#print("MDC-I: Display: showLCDInfo: file_index: %s, len(file_list): %s, slideshow_active: %s" % (self.file_index, len(self.file_list), self.slideshow_active))
		path = self.file[FILE_PATH]
		adir = os.path.basename(os.path.dirname(path))
		direction = "> " if self.direction else "< "
		if not self.slideshow_active:
			direction = ""
		self.displayLCD("%s%d/%d" % (direction, self.file_index + 1, len(self.file_list)), adir)

### slide functions

	def nextSlide(self):
		#print("MDC: MediaPlayer: MDCMediaPlayer: nextSlide")
		self.slideTimer.stop()
		self.stopVideo()
		if self.direction:
			self.file_index = nextIndex(self.file_index, len(self.file_list))
		else:
			self.file_index = previousIndex(self.file_index, len(self.file_list))
		self.file = self.file_list[self.file_index]
		DelayTimer(20, self.showSlide)

	def showSlide(self):
		print("MDC-I: MediaPlayer: MDCMediaPlayer: showSlide: file_index: %s, len(self.file_list): %s" % (self.file_index, len(self.file_list)))
		if self.file[FILE_MEDIA] == "picture":
			self.show()
			if self.external_slideshow and self.slideshow_active:
				self["image"].setPicture(self.file[FILE_PATH])
			else:
				self.unhidePicture()
				self.showPicture(self.file[FILE_PATH])
			if self.slideshow_active:
				self.slideTimer.start(self.slideshow_duration, True)
		elif self.file[FILE_MEDIA] == "movie":
			self.hide()
			self.showVideo(self.file[FILE_PATH])
		else:
			self.nextSlide()
		self.showLCDInfo()

### picture functions

	def showPicture(self, path):
		#print("MDC: MediaPlayer: MDCMediaPlayer: showPicture: show picture: path: %s, index: %s" % (path, self.file_index))
		path = getPicturePath(path)
		self["picture"].instance.setPixmap(gPixmapPtr())
		picture = LoadPixmap(path, cached=False)
		self["picture"].instance.setPixmap(picture)

	def hidePicture(self):
		self["picture"].hide()
		self["picture_background"].hide()

	def unhidePicture(self):
		self["picture"].show()
		self["picture_background"].show()

### video functions

	def showVideo(self, filename):
		print("MDC-I: MediaPlayer: MDCMediaPlayer: showVideo: filename: %s" % filename)
		self["picture"].instance.setPixmap(gPixmapPtr())
		cmd = "gst-launch-1.0 playbin -v uri='file://%s'" % filename
		if self.song_list:
			cmd += ' flags=0x51'
		#print("MDC: MediaPlayer: MDCMediaPlayer: showVideo: cmd: %s" % cmd)
		self.video_container.execute(cmd)

	def showVideoCallback(self):
		#print("MDC: MediaPlayer: MDCMediaPlayer: showVideoCallback: slideshow_active: %s" % self.slideshow_active)
		if self.slideshow_active:
			self.nextSlide()

	def stopVideo(self):
		#print("MDC: MediaPlayer: stopVideo: media: %s" % self.file[FILE_MEDIA])
		if self.file[FILE_MEDIA] == "movie":
			self.video_container.kill()
			if self.slideshow_active:
				self.blackScreen()

	def blackScreen(self):
		filename = getSkinPath("images/black.mvi")
		cmd = "showiframe %s" % filename
		#print("MDC: MediaPlayer: MDCMediaPlayer: blackScreen: cmd: %s" % cmd)
		self.black_container.execute(cmd)

### external slideshow

	def toggleTransitionMode(self):
		max_animations = len(ext_slideshow_animations) if self.external_slideshow else len(ext_slideshow_animations) + len(int_slideshow_animations)
		self.animation = (self.animation + 1) % max_animations
		self.animation = int(self.slideshow_animations[0][0]) if self.animation < int(self.slideshow_animations[0][0]) else self.animation
		#print("MDC: MediaPlayer: toggleTransitionMode: animation: %s" % self.animation)
		self.setSlideshowAnimation(self.animation)

		sanimation = "n/a"
		for animation in self.slideshow_animations:
			if animation[0] == str(self.animation):
				sanimation = animation[1]
				break
		if self.toast is not None:
			self.session.toastManager.hide(self.toast)
		self.toast = self.session.toastManager.showToast(_("Animation") + " " + str(self.animation) + ": " + sanimation)

	def imageChanged(self):
		#print("MDC: MediaPlayer: imageChanged")
		self.hidePicture()

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

### file functions

	def rotatePicture(self):
		#print("MDC: MediaPlayer: MDCMediaPlayer: rotatePicture: file_index: %s" % self.file_index)
		if self.file[FILE_MEDIA] == "picture":
			path = self.file[FILE_PATH]
			filename, ext = os.path.splitext(path)
			out_file = in_file = filename + ".transformed" + ext
			if not os.path.exists(in_file):
				in_file = path
			rc = rotatePicture(in_file, out_file, 90)
			if rc:
				createThumbnail(path, (self.thumbnail_size.width(), self.thumbnail_size.height()), True)

				orientation = self.file[FILE_META]["Orientation"]
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
				self.file[FILE_META]["Orientation"] = new_orientation
				saveMeta(path, self.file)
				if new_orientation == 1:
					deleteFile(out_file)

			self.showPicture(path)

### key functions

	def exit(self):
		self.stopVideo()
		self.stopSong()
		config.plugins.mediacockpit.animation.value = str(self.animation)
		config.plugins.mediacockpit.animation.save()
		path = self.file[FILE_PATH]
		#print("MDC: MediaPlayer: MDCMediaPlayer: exit: file_index: %s, path: %s" % (self.file_index, path))
		self.close(path)

	def yellow(self):
		if self.toast is not None:
			self.session.toastManager.hide(self.toast)
		self.session.toastManager.showToast(_("Rotating picture..."))
		self.rotatePicture()

	def right(self):
		self.direction = True
		self.nextSlide()

	def left(self):
		self.direction = False
		self.nextSlide()

	def stop(self):
		if self.file[FILE_MEDIA] == "movie":
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
			self.showSlide()
		else:
			self.slideTimer.stop()
			self.stopVideo()
			self.showLCDInfo()

	def openInfo(self):
		if not self.slideshow_active and self.file[FILE_TYPE] == TYPE_FILE:
			self.session.openWithCallback(self.openInfoCallback, MediaInfo, self.file_list, self.file_index)

	def openInfoCallback(self, file_index):
		self.file_index = file_index
		self.LayoutFinish()
