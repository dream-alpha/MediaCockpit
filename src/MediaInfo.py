#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2020 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
#      This program is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      This program is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      For more information on the GNU General Public License see:
#      <http://www.gnu.org/licenses/>.


import os
from __init__ import _
from datetime import datetime
from enigma import eConsoleAppContainer
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.Sources.List import List
from Components.ActionMap import HelpableActionMap
from MetaFile import FILE_PATH, FILE_MEDIA, FILE_DATE
from PictureUtils import getExifData
from SkinUtils import getSkinPath
from Tools.LoadPixmap import LoadPixmap
from Display import Display


class MediaInfo(Display, Screen, HelpableScreen):

	def __init__(self, session, file_list, file_index):
		self.file_list = file_list
		self.file_index = file_index
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = ["MDCMediaInfo"]
		Display.__init__(self)

		self["actions"] = HelpableActionMap(
			self,
			"MDCActions",
			{
				"ok":		(self.exit,		_("Exit")),
				"right":	(self.moveRight,	_("Next picture")),
				"left":		(self.moveLeft,		_("Previous picture")),
				"exit":		(self.exit,		_("Exit")),
				"red":		(self.red,		_("Exit")),
				"green":	(self.green,		_("Exit")),
				"blue":		(self.blue,		_("Thumbnail"))
			},
			prio=-1
		)

		self.thumbnail = None
		self.setTitle(_("Media Infos"))
		self["list"] = List()
		self["icon"] = Pixmap()
		self["thumbnail"] = Pixmap()
		self["key_green"] = Button(_("Ok"))
		self["key_red"] = Button(_("Cancel"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button(_("Thumbnail"))
		self.container = eConsoleAppContainer()
		self.container_appClosed_conn = self.container.appClosed.connect(self.grabThumbnailCallback)
		self.onLayoutFinish.append(self.firstStart)

	def firstStart(self):
		self.fillList()

	def moveLeft(self):
		self.file_index -= 1
		if self.file_index < 0:
			self.file_index = len(self.file_list) - 1
		self.fillList()

	def moveRight(self):
		self.file_index += 1
		if self.file_index > len(self.file_list) - 1:
			self.file_index = 0
		self.fillList()

	def exit(self):
		self.close(self.file_index)

	def red(self):
		self.exit()

	def green(self):
		self.exit()

	def yellow(self):
		pass

	def blue(self):
		self.grabThumbnail()

	def grabThumbnail(self):
		if self.file[FILE_MEDIA] == "movie" and not self.container.running():
			self["key_blue"].hide()
			filename, _ext = os.path.splitext(self.file[FILE_PATH])
			self.thumbnail = filename + ".thumbnail.jpg"
			cmd = "ffmpeg -v quiet -i '%s' -ss %d -vf scale=320:-1 -vframes 1 '%s' -y" % (self.file[FILE_PATH], 0.5, self.thumbnail)
			self.container.execute(cmd)

	def grabThumbnailCallback(self, retval):
		self["key_blue"].show()
		if retval == 0 and os.path.exists(self.thumbnail):
			self.showThumbnail(self.thumbnail)

	def fillList(self):
		self.file = self.file_list[self.file_index]
		self.displayLCD("%d/%d" % (self.file_index + 1, len(self.file_list)), os.path.basename(self.file[FILE_PATH]))
		self["thumbnail"].hide()
		ptr = LoadPixmap(getSkinPath("images/" + self.file[FILE_MEDIA] + ".svg"), cached=False)
		self["icon"].instance.setPixmap(ptr)
		self["icon"].show()
		alist = []
		alist.append((_("Directory"), os.path.dirname(self.file[FILE_PATH]), None))
		alist.append((_("Filename"), os.path.basename(self.file[FILE_PATH]), None))
		date_time = datetime.fromtimestamp(self.file[FILE_DATE]).strftime("%Y-%m-%d %H:%M:%S")
		alist.append((_("Date"), date_time, None))
		alist.append(("", "", None))
		filename, ext = os.path.splitext(self.file[FILE_PATH])
		if self.file[FILE_MEDIA] == "picture":
			self["key_blue"].hide()
			exif_data = getExifData(self.file[FILE_PATH])
			#print("MDC: MediaInfo: fillList: exif_data: %s" % str(exif_data))
			thumbnail = filename + ".thumbnail" + ext
			self.showThumbnail(thumbnail)
			MeteringModeDesc = (_("unknown"), "Average", "Center-weighted Average", "Spot", "Multi-spot", "Multi-segment", "Partial", "Other")
			OrientDesc = ("Top-Left(0)", "Top-Left(1)", "Top-Right", "Bottom-Right", "Bottom-Left", "Left-Top", "Right-Top", "Right-Bottom", "Left-Bottom")
			ExposureProgram = (_("not defined"), "Manual", "Program", "Aperture priority", "Shutter priority", "Creative", "Action", "Portrait", "Landscape")

			if "Model" in exif_data:
				alist.append((_("Model"), exif_data["Model"], None))
			if "Producer" in exif_data:
				alist.append((_("Producer"), exif_data["Producer"], None))
			if "DateTimeOriginal" in exif_data:
				alist.append((_("Date") + "/" + _("Time"), exif_data["DateTimeOriginal"], None))
			if "ExifImageWidth" in exif_data and "ExifImageHeight" in exif_data:
				alist.append((_("Width") + "/" + _("Height"), "%dx%d" % (exif_data["ExifImageWidth"], exif_data["ExifImageHeight"]), None))
			if "Orientation" in exif_data:
				alist.append((_("Orientation"), OrientDesc[exif_data["Orientation"]], None))
			if "Flash" in exif_data:
				alist.append((_("Flash"), str(exif_data["Flash"]), None))
			if "MeteringMode" in exif_data:
				alist.append((_("Metering Mode"), MeteringModeDesc[exif_data["MeteringMode"]], None))
			if "ISOSpeedRating" in exif_data:
				alist.append((_("ISO Speed Rating"), exif_data["ISOSpeedRating"], None))
			if "PhotographicSensitivity" in exif_data:
				alist.append((_("Photographic Sensitivity"), exif_data["PhotographicSensitivity"], None))
			if "ExposureProgram" in exif_data:
				alist.append((_("Exposure Program"), ExposureProgram[exif_data["ExposureProgram"]], None))
			if "Software" in exif_data:
				alist.append((_("Software"), exif_data["Software"], None))
			if "GPSAltitude" in exif_data:
				alist.append((_("GPS Altitude"), exif_data["GPSAltitude"], None))
			if "GPSLatitude" in exif_data and "GPSLongitude" in exif_data:
				alist.append((_("GPS Latitude"), exif_data["GPSLatitude"], None))
				alist.append((_("GPS Longitude"), exif_data["GPSLongitude"], None))
			if "ExifVersion" in exif_data:
				alist.append((_("Exif Version"), exif_data["ExifVersion"], None))
		elif self.file[FILE_MEDIA] == "movie":
			self["key_blue"].show()
			thumbnail = filename + ".thumbnail.jpg"
			self.showThumbnail(thumbnail)
		self["list"].setList(alist)
		self["list"].master.downstream_elements.setSelectionEnabled(0)

	def showThumbnail(self, path):
		if os.path.exists(path):
			ptr = LoadPixmap(path, cached=False)
			self["thumbnail"].instance.setPixmap(ptr)
			self["thumbnail"].show()
			self["icon"].hide()
