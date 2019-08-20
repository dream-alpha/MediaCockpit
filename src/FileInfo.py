#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2019 by dream-alpha
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
from enigma import eConsoleAppContainer, ePicLoad
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Components.AVSwitch import AVSwitch
from Components.Pixmap import Pixmap
from Components.Button import Button
from Components.Sources.List import List
from Components.ActionMap import HelpableActionMap
from globals import FILE_PATH, FILE_MEDIA
from PictureUtils import getExifData, rotatePictureExif
from SkinUtils import getSkinPath
from Tools.LoadPixmap import LoadPixmap


class FileInfo(Screen, HelpableScreen):

	def __init__(self, session, file_list, file_index):
		self.file_list = file_list
		self.file_index = file_index
		Screen.__init__(self, session)
		HelpableScreen.__init__(self)
		self.skinName = ["MDCFileInfo"]

		self["actions"] = HelpableActionMap(
			self,
			"MDCActions",
			{
				"ok":		(self.KeyExit,		_("Exit")),
				"green":	(self.KeyExit,		_("Exit")),
				"right":	(self.KeyRight,		_("Next picture")),
				"left":		(self.KeyLeft,		_("Previous picture")),
				"exit":		(self.KeyExit,		_("Exit")),
				"red":		(self.KeyExit,		_("Exit")),
				"blue":		(self.grabThumbnail,	_("Thumbnail"))
			},
			prio=-1
		)

		self.thumbnail = ""
		self.reload_tiles = False
		self.setTitle(_("Media Infos"))
		self["list"] = List()
		self["icon"] = Pixmap()
		self["thumbnail"] = Pixmap()
		self["key_green"] = Button(_("Ok"))
		self["key_red"] = Button(_("Cancel"))
		self["key_yellow"] = Button()
		self["key_blue"] = Button(_("Thumbnail"))
		self.picload = ePicLoad()
		self.picload_conn = self.picload.PictureData.connect(self.decodePicture)
		self.container = eConsoleAppContainer()
		self.container_appClosed_conn = self.container.appClosed.connect(self.grabThumbnailCallback)
		self.onLayoutFinish.append(self.firstStart)

	def firstStart(self):
		scale = AVSwitch().getFramebufferScale()
		self.picload.setPara(
			[
				self["thumbnail"].instance.size().width(),
				self["thumbnail"].instance.size().height(),
				scale[0],
				scale[1],
				0,
				1,
				"#ff000000"
			]
		)
		self.fillList()

	def KeyLeft(self):
		self.file_index -= 1
		if self.file_index < 0:
			self.file_index = len(self.file_list) - 1
		self.fillList()

	def KeyRight(self):
		self.file_index += 1
		if self.file_index > len(self.file_list) - 1:
			self.file_index = 0
		self.fillList()

	def KeyExit(self):
		self.close(self.reload_tiles, self.file_index)

	def grabThumbnail(self):
		if self.file[FILE_MEDIA] == "movie" and not self.container.running():
			self["key_blue"].hide()
			self.thumbnail = self.file[FILE_PATH] + ".thumbnail.jpg"
			cmd = "ffmpeg -v quiet -i '%s' -ss %d -vf scale=320:-1 -vframes 1 '%s' -y" % (self.file[FILE_PATH], 0.5, self.thumbnail)
			self.container.execute(cmd)

	def grabThumbnailCallback(self, retval):
		self["key_blue"].show()
		if retval == 0 and os.path.exists(self.thumbnail):
			self.reload_tiles = True
			self.picload.startDecode(self.thumbnail)

	def fillList(self):
		self.file = self.file_list[self.file_index]
		self["thumbnail"].hide()
		ptr = LoadPixmap(path=getSkinPath("images/" + self.file[FILE_MEDIA] + ".svg"), cached=False)
		self["icon"].instance.setPixmap(ptr)
		self["icon"].show()
		alist = []
		alist.append((_("Directory"), os.path.dirname(self.file[FILE_PATH]), None))
		alist.append((_("Filename"), os.path.basename(self.file[FILE_PATH]), None))
		#date_time = datetime.fromtimestamp(self.file[FILE_DATE]).strftime("%Y:%m:%d %H:%M:%S")
		#alist.append((_("Date"), date_time, None))
		if self.file[FILE_MEDIA] == "picture":
			self["key_blue"].hide()
			meta_data = getExifData(self.file[FILE_PATH])
			if meta_data:
				#print("MDC: FileInfo: fillList: meta_data: %s" % str(meta_data))
				tmpfile = rotatePictureExif(self.file[FILE_PATH], meta_data)
				self.picload.startDecode(tmpfile)
				MeteringModeDesc = (_("unknown"), "Average", "Center-weighted Average", "Spot", "Multi-spot", "Multi-segment", "Partial", "Other")
				OrientDesc = ("Top-Left(0)", "Top-Left(1)", "Top-Right", "Bottom-Right", "Bottom-Left", "Left-Top", "Right-Top", "Right-Bottom", "Left-Bottom")
				ExposureProgram = (_("not defined"), "Manual", "Program", "Aperture priority", "Shutter priority", "Creative", "Action", "Portrait", "Landscape")

				if "Model" in meta_data:
					alist.append((_("Model"), meta_data["Model"], None))
				if "Producer" in meta_data:
					alist.append((_("Producer"), meta_data["Producer"], None))
				if "DateTimeOriginal" in meta_data:
					alist.append((_("Date") + "/" + _("Time"), meta_data["DateTimeOriginal"], None))
				if "ExifImageWidth" in meta_data and "ExifImageHeight" in meta_data:
					alist.append((_("Width") + "/" + _("Height"), "%dx%d" % (meta_data["ExifImageWidth"], meta_data["ExifImageHeight"]), None))
				if "Orientation" in meta_data:
					alist.append((_("Orientation"), OrientDesc[meta_data["Orientation"]], None))
				if "Flash" in meta_data:
					alist.append((_("Flash"), str(meta_data["Flash"]), None))
				if "MeteringMode" in meta_data:
					alist.append((_("Metering Mode"), MeteringModeDesc[meta_data["MeteringMode"]], None))
				if "ISOSpeedRating" in meta_data:
					alist.append((_("ISO Speed Rating"), meta_data["ISOSpeedRating"], None))
				if "PhotographicSensitivity" in meta_data:
					alist.append((_("Photographic Sensitivity"), meta_data["PhotographicSensitivity"], None))
				if "ExposureProgram" in meta_data:
					alist.append((_("Exposure Program"), ExposureProgram[meta_data["ExposureProgram"]], None))
				if "Software" in meta_data:
					alist.append((_("Software"), meta_data["Software"], None))
				if "GPSAltitude" in meta_data:
					alist.append((_("GPS Altitude"), meta_data["GPSAltitude"], None))
				if "GPSLatitude" in meta_data and "GPSLongitude" in meta_data:
					alist.append((_("GPS Latitude"), meta_data["GPSLatitude"], None))
					alist.append((_("GPS Longitude"), meta_data["GPSLongitude"], None))
				if "ExifVersion" in meta_data:
					alist.append((_("Exif Version"), meta_data["ExifVersion"], None))
		elif self.file[FILE_MEDIA] == "movie":
			self["key_blue"].show()
			thumbnail = self.file[FILE_PATH] + ".thumbnail.jpg"
			if os.path.exists(thumbnail):
				self.picload.startDecode(thumbnail)
		self["list"].setList(alist)
		self["list"].master.downstream_elements.setSelectionEnabled(0)

	def decodePicture(self, _picInfo):
		ptr = self.picload.getData()
		if ptr is not None:
			self["thumbnail"].instance.setPixmap(ptr)
			self["thumbnail"].show()
			self["icon"].hide()
