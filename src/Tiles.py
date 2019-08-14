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
from Components.Label import Label
from Components.Pixmap import Pixmap
from Tools.BoundFunction import boundFunction
from Components.config import config
from enigma import eSize, ePoint, gFont, ePicLoad
from PictureUtils import rotatePictureExif
from SkinUtils import getSkinPath
from Tools.LoadPixmap import LoadPixmap
from skin import parseColor
from Screens.Screen import Screen
from DelayedFunction import DelayedFunction


class Tiles(Screen, object):

	def __init__(self):
		self.tile_columns = 5
		self.tile_rows = 3
		self.tiles = self.tile_columns * self.tile_rows
		self.picLoads = []

		self.selection_size_offset = config.plugins.mediacockpit.selection_size_offset.value
		self.selection_font_offset = config.plugins.mediacockpit.selection_font_offset.value
		self.normal_background_color = parseColor(config.plugins.mediacockpit.normal_background_color.value)
		self.selection_background_color = parseColor(config.plugins.mediacockpit.selection_background_color.value)
		self.normal_foreground_color = parseColor(config.plugins.mediacockpit.normal_foreground_color.value)
		self.selection_foreground_color = parseColor(config.plugins.mediacockpit.selection_foreground_color.value)
		self.selection_frame_color = parseColor(config.plugins.mediacockpit.selection_frame_color.value)

		for tile_pos in range(self.tiles):
			self["BGFrame%d" % tile_pos] = Label()
			self["BGFrame%d" % tile_pos].hide()
			self["BGLabel%d" % tile_pos] = Label()
			self["Picture%d" % tile_pos] = Pixmap()
			self["TXLabel%d" % tile_pos] = Label()
			self.picLoads.append(ePicLoad())

		self.icons = {}
		self.icons["picture"] = LoadPixmap(path=getSkinPath("images/" + "picture.svg"), cached=True)
		self.icons["movie"] = LoadPixmap(path=getSkinPath("images/" + "movie.svg"), cached=True)
		self.icons["music"] = LoadPixmap(path=getSkinPath("images/" + "music.svg"), cached=True)
		self.icons["folder"] = LoadPixmap(path=getSkinPath("images/" + "folder.svg"), cached=True)
		self.icons["playlist"] = LoadPixmap(path=getSkinPath("images/" + "playlist.svg"), cached=True)
		self.icons["goup"] = LoadPixmap(path=getSkinPath("images/" + "goup.svg"), cached=True)

		self.current_page = -1
		self.last_tile_pos = -1

	def getTiles(self):
		return self.tiles

	def initTileAttribs(self):
		#print("MDC: Tiles: initTileAttribs")
		self.thumbnail_size = self["Picture0"].instance.size()

		for tile_pos in range(self.tiles):
			self["BGLabel%d" % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
			self["BGLabel%d" % tile_pos].instance.setBackgroundColor(self.normal_background_color)
			self["TXLabel%d" % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
			self["TXLabel%d" % tile_pos].instance.setBackgroundColor(self.normal_background_color)
			self["BGFrame%d" % tile_pos].instance.setBackgroundColor(self.selection_frame_color)

			self.picLoads[tile_pos].setPara((self.thumbnail_size.width(), self.thumbnail_size.height(), self.sc[0], self.sc[1], 0, 1, "background"))

		font = self["TXLabel0"].instance.getFont()
		self.font_family = font.family
		self.font_size = font.pointSize

		self.thumbnail_size = self["Picture0"].instance.size()

	def selectTile(self, tile_pos):
		print("MDC-I: Tiles: selectTile: tile_pos: %s, last_tile_pos: %s" % (tile_pos, self.last_tile_pos))
		if self.last_tile_pos < 0 and tile_pos >= 0:
			if config.plugins.mediacockpit.frame.value:
				self["BGFrame%d" % tile_pos].show()
			size = self["BGFrame%d" % tile_pos].instance.size()
			pos = self["BGFrame%d" % tile_pos].instance.position()
			self["BGFrame%d" % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height() + self.selection_size_offset * 2))
			self["BGFrame%d" % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() - self.selection_size_offset))
			size = self["BGLabel%d" % tile_pos].instance.size()
			pos = self["BGLabel%d" % tile_pos].instance.position()
			self["BGLabel%d" % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height() + self.selection_size_offset * 2))
			self["BGLabel%d" % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() - self.selection_size_offset))
			self["BGLabel%d" % tile_pos].instance.setBackgroundColor(self.selection_background_color)
			self["BGLabel%d" % tile_pos].instance.setForegroundColor(self.selection_foreground_color)
			size = self["Picture%d" % tile_pos].instance.size()
			pos = self["Picture%d" % tile_pos].instance.position()
			self["Picture%d" % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height() + self.selection_size_offset * 2))
			self["Picture%d" % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() - self.selection_size_offset))
			size = self["TXLabel%d" % tile_pos].instance.size()
			pos = self["TXLabel%d" % tile_pos].instance.position()
			self["TXLabel%d" % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height()))
			self["TXLabel%d" % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() + self.selection_size_offset))
			self["TXLabel%d" % tile_pos].instance.setFont(gFont(self.font_family, self.font_size + self.selection_font_offset))
			self["TXLabel%d" % tile_pos].instance.setBackgroundColor(self.selection_background_color)
			self["TXLabel%d" % tile_pos].instance.setForegroundColor(self.selection_foreground_color)
			self.last_tile_pos = tile_pos

	def unselectTile(self, tile_pos):
		print("MDC-I: Tiles: unselectTile: tile_pos: %s, last_tile_pos: %s" % (tile_pos, self.last_tile_pos))
		if self.last_tile_pos > -1 and tile_pos >= 0:
			self["BGFrame%d" % tile_pos].hide()
			size = self["BGFrame%d" % tile_pos].instance.size()
			pos = self["BGFrame%d" % tile_pos].instance.position()
			self["BGFrame%d" % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height() - self.selection_size_offset * 2))
			self["BGFrame%d" % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() + self.selection_size_offset))
			size = self["BGLabel%d" % tile_pos].instance.size()
			pos = self["BGLabel%d" % tile_pos].instance.position()
			self["BGLabel%d" % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height() - self.selection_size_offset * 2))
			self["BGLabel%d" % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() + self.selection_size_offset))
			self["BGLabel%d" % tile_pos].instance.setBackgroundColor(self.normal_background_color)
			self["BGLabel%d" % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
			size = self["Picture%d" % tile_pos].instance.size()
			pos = self["Picture%d" % tile_pos].instance.position()
			self["Picture%d" % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height() - self.selection_size_offset * 2))
			self["Picture%d" % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() + self.selection_size_offset))
			size = self["TXLabel%d" % tile_pos].instance.size()
			pos = self["TXLabel%d" % tile_pos].instance.position()
			self["TXLabel%d" % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height()))
			self["TXLabel%d" % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() - self.selection_size_offset))
			self["TXLabel%d" % tile_pos].instance.setFont(gFont(self.font_family, self.font_size))
			self["TXLabel%d" % tile_pos].instance.setBackgroundColor(self.normal_background_color)
			self["TXLabel%d" % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
			self.last_tile_pos = -1

	def hideTiles(self):
		self.unselectTile(self.last_tile_pos)
		for tile_pos in range(self.tiles):
			self["Picture%d" % tile_pos].hide()
			self["TXLabel%d" % tile_pos].hide()
			self["BGLabel%d" % tile_pos].show()
			self["BGFrame%d" % tile_pos].hide()

	def paintTiles(self, refresh_tiles=False):
		print("MDC-I: Tiles: paintTiles: current_page: %s, file_index: %s" % (self.current_page, self.file_index))
		page = self.file_index / self.tiles
		if page != self.current_page or refresh_tiles:
			self.current_page = page
			first_idx = self.current_page * self.tiles
			last_idx = (self.current_page + 1) * self.tiles
			#print("MDC: Tiles: paintTiles: first_idx: %s, last_idx: %s" % (first_idx, last_idx))
			for idx in range(first_idx, last_idx):
				tile_pos = idx % self.tiles
				if idx < len(self.file_list):
					path, _type, _date, media, _meta = self.file_list[idx]
					self["BGLabel%d" % tile_pos].show()
					self["TXLabel%d" % tile_pos].setText(os.path.basename(path))
					self["TXLabel%d" % tile_pos].show()
					if not refresh_tiles:
						self["Picture%d" % tile_pos].instance.setPixmap(self.icons[media])
						self["Picture%d" % tile_pos].show()
				else:
					self["BGLabel%d" % tile_pos].hide()
					self["Picture%d" % tile_pos].hide()
					self["TXLabel%d" % tile_pos].hide()
					self["BGFrame%d" % tile_pos].hide()
			DelayedFunction(10, self.paintThumbnails, first_idx, last_idx)

		tile_pos = self.file_index % self.tiles
		#print("MDC: Tiles: paintTiles: tile_pos: %s, last_tile_pos: %s" % (tile_pos, self.last_tile_pos))
		self.unselectTile(self.last_tile_pos)
		self.selectTile(tile_pos)

	def paintThumbnails(self, idx, last_idx):
		tile_pos = idx % self.tiles
		page = idx / self.tiles
		path, _type, _date, media, meta = self.file_list[idx]
		if media == "picture":
			path = rotatePictureExif(path, meta)
			self.paintThumbnail(page, tile_pos, path)
		elif media == "movie":
			thumbnail = path + ".thumbnail.jpg"
			if os.path.exists(thumbnail):
				path = thumbnail
				self.paintThumbnail(page, tile_pos, path)
		idx += 1
		if idx < last_idx and idx < len(self.file_list):
			DelayedFunction(10, self.paintThumbnails, idx, last_idx)

	def paintThumbnail(self, page, tile_pos, path):
		#print("MDC: Tiles: paintThumbnail: page: %s, tile_pos: %s, path: %s" % (page, tile_pos, path))
		self.picLoads[tile_pos].conn = self.picLoads[tile_pos].PictureData.connect(boundFunction(self.paintThumbnailCallback, page, tile_pos))
		self.picLoads[tile_pos].getThumbnail(path)

	def paintThumbnailCallback(self, page, tile_pos, _info):
		#print("MDC: Tiles: paintThumbnailCallback: page: %s, current_page: %s, tile_pos: %s" % (page, self.current_page, tile_pos))
		if page == self.current_page:
			ptr = self.picLoads[tile_pos].getData()
			self["Picture%d" % tile_pos].instance.setPixmap(ptr)
