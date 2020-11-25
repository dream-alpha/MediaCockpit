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
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import config
from enigma import eSize, ePoint, gFont
from SkinUtils import getSkinPath
from Tools.LoadPixmap import LoadPixmap
from skin import parseColor
from MetaFile import FILE_TYPE, FILE_PATH, TYPE_FILE


class Tiles():

	def __init__(self):
		self.tile_columns = 5
		self.tile_rows = 3
		self.file_list = []
		self.current_path = None
		self.tiles = self.tile_columns * self.tile_rows

		self.selection_size_offset = config.plugins.mediacockpit.selection_size_offset.value
		self.selection_font_offset = config.plugins.mediacockpit.selection_font_offset.value
		self.normal_background_color = parseColor(config.plugins.mediacockpit.normal_background_color.value)
		self.selection_background_color = parseColor(config.plugins.mediacockpit.selection_background_color.value)
		self.normal_foreground_color = parseColor(config.plugins.mediacockpit.normal_foreground_color.value)
		self.selection_foreground_color = parseColor(config.plugins.mediacockpit.selection_foreground_color.value)
		self.selection_frame_color = parseColor(config.plugins.mediacockpit.selection_frame_color.value)

		for tile_pos in range(self.tiles):
			self["Frame%d" % tile_pos] = Label()
			self["Frame%d" % tile_pos].hide()
			self["Tile%d" % tile_pos] = Label()
			self["Picture%d" % tile_pos] = Pixmap()
			self["Icon%d" % tile_pos] = Pixmap()
			self["Text%d" % tile_pos] = Label()

		self.icons = {}
		self.icons["picture"] = LoadPixmap(getSkinPath("images/" + "picture.svg"), cached=True)
		self.icons["movie"] = LoadPixmap(getSkinPath("images/" + "movie.svg"), cached=True)
		self.icons["music"] = LoadPixmap(getSkinPath("images/" + "music.svg"), cached=True)
		self.icons["folder"] = LoadPixmap(getSkinPath("images/" + "folder.svg"), cached=True)
		self.icons["playlist"] = LoadPixmap(getSkinPath("images/" + "playlist.svg"), cached=True)
		self.icons["goup"] = LoadPixmap(getSkinPath("images/" + "goup.svg"), cached=True)

		self.busy = False
		self.last_tile_pos = -1

	def initTileAttribs(self):
		#print("MDC: Tiles: initTileAttribs")
		self.thumbnail_size = self["Picture0"].instance.size()

		for tile_pos in range(self.tiles):
			self["Tile%d" % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
			self["Tile%d" % tile_pos].instance.setBackgroundColor(self.normal_background_color)
			self["Text%d" % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
			self["Text%d" % tile_pos].instance.setBackgroundColor(self.normal_background_color)
			self["Frame%d" % tile_pos].instance.setBackgroundColor(self.selection_frame_color)

		font = self["Text0"].instance.getFont()
		self.font_family = font.family
		self.font_size = font.pointSize

	def selectTile(self, tile_pos):
		#print("MDC: Tiles: selectTile: tile_pos: %s, last_tile_pos: %s" % (tile_pos, self.last_tile_pos))
		if self.last_tile_pos < 0 and tile_pos >= 0 and self.file_list:
			if config.plugins.mediacockpit.frame.value:
				self["Frame%d" % tile_pos].show()
			size = self["Frame%d" % tile_pos].instance.size()
			pos = self["Frame%d" % tile_pos].instance.position()
			self["Frame%d" % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height() + self.selection_size_offset * 2))
			self["Frame%d" % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() - self.selection_size_offset))
			size = self["Tile%d" % tile_pos].instance.size()
			pos = self["Tile%d" % tile_pos].instance.position()
			self["Tile%d" % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height() + self.selection_size_offset * 2))
			self["Tile%d" % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() - self.selection_size_offset))
			self["Tile%d" % tile_pos].instance.setBackgroundColor(self.selection_background_color)
			self["Tile%d" % tile_pos].instance.setForegroundColor(self.selection_foreground_color)
			size = self["Picture%d" % tile_pos].instance.size()
			pos = self["Picture%d" % tile_pos].instance.position()
			self["Picture%d" % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height() + self.selection_size_offset * 2))
			self["Picture%d" % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() - self.selection_size_offset))
			size = self["Icon%d" % tile_pos].instance.size()
			pos = self["Icon%d" % tile_pos].instance.position()
			self["Icon%d" % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height() + self.selection_size_offset * 2))
			self["Icon%d" % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() - self.selection_size_offset))
			size = self["Text%d" % tile_pos].instance.size()
			pos = self["Text%d" % tile_pos].instance.position()
			self["Text%d" % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height()))
			self["Text%d" % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() + self.selection_size_offset))
			self["Text%d" % tile_pos].instance.setFont(gFont(self.font_family, self.font_size + self.selection_font_offset))
			self["Text%d" % tile_pos].instance.setBackgroundColor(self.selection_background_color)
			self["Text%d" % tile_pos].instance.setForegroundColor(self.selection_foreground_color)
			self.last_tile_pos = tile_pos

	def unselectTile(self, tile_pos):
		#print("MDC: Tiles: unselectTile: tile_pos: %s, last_tile_pos: %s" % (tile_pos, self.last_tile_pos))
		if self.last_tile_pos > -1 and tile_pos >= 0:
			self["Frame%d" % tile_pos].hide()
			size = self["Frame%d" % tile_pos].instance.size()
			pos = self["Frame%d" % tile_pos].instance.position()
			self["Frame%d" % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height() - self.selection_size_offset * 2))
			self["Frame%d" % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() + self.selection_size_offset))
			size = self["Tile%d" % tile_pos].instance.size()
			pos = self["Tile%d" % tile_pos].instance.position()
			self["Tile%d" % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height() - self.selection_size_offset * 2))
			self["Tile%d" % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() + self.selection_size_offset))
			self["Tile%d" % tile_pos].instance.setBackgroundColor(self.normal_background_color)
			self["Tile%d" % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
			size = self["Picture%d" % tile_pos].instance.size()
			pos = self["Picture%d" % tile_pos].instance.position()
			self["Picture%d" % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height() - self.selection_size_offset * 2))
			self["Picture%d" % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() + self.selection_size_offset))
			size = self["Icon%d" % tile_pos].instance.size()
			pos = self["Icon%d" % tile_pos].instance.position()
			self["Icon%d" % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height() - self.selection_size_offset * 2))
			self["Icon%d" % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() + self.selection_size_offset))
			size = self["Text%d" % tile_pos].instance.size()
			pos = self["Text%d" % tile_pos].instance.position()
			self["Text%d" % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height()))
			self["Text%d" % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() - self.selection_size_offset))
			self["Text%d" % tile_pos].instance.setFont(gFont(self.font_family, self.font_size))
			self["Text%d" % tile_pos].instance.setBackgroundColor(self.normal_background_color)
			self["Text%d" % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
		self.last_tile_pos = -1

	def displayLCD(self, _file_of_files, _path):
		print("MDC-E: Tiles: displayLCD: overridden in child class")

	def displayOSD(self, _msg):
		print("MDC-E: Tiles: displayOSD: overridden in child class")

	def hideTile(self, tile_pos):
		self["Picture%d" % tile_pos].hide()
		self["Icon%d" % tile_pos].hide()
		self["Text%d" % tile_pos].hide()
		self["Tile%d" % tile_pos].hide()
		self["Frame%d" % tile_pos].hide()

	def hideTiles(self):
		self.unselectTile(self.last_tile_pos)
		for tile_pos in range(self.tiles):
			self.hideTile(tile_pos)

	def paintTile(self, idx, tile_pos):
		#print("MDC: FileList: paintTile: idx: %s, tile_pos: %s" % (idx, tile_pos))
		path, _type, _date, media, _meta = self.file_list[idx]
		self["Tile%d" % tile_pos].show()
		self["Text%d" % tile_pos].setText(os.path.basename(path))
		filename, ext = os.path.splitext(path)
		thumbnail_path = None
		for thumbnail in [filename + ".thumbnail" + ext, filename + ".thumbnail.jpg"]:
			if os.path.exists(thumbnail):
				thumbnail_path = thumbnail
				break
		if thumbnail_path:
			self["Picture%d" % tile_pos].instance.setPixmap(LoadPixmap(thumbnail_path, cached=False))
			self["Icon%d" % tile_pos].hide()
			self["Text%d" % tile_pos].hide()
			self["Picture%d" % tile_pos].show()
		else:
			self["Picture%d" % tile_pos].hide()
			self["Icon%d" % tile_pos].instance.setPixmap(self.icons[media])
			self["Icon%d" % tile_pos].show()
			self["Text%d" % tile_pos].show()

	def paintTiles(self, is_mounted=True):
		print("MDC-I: Tiles: paintTiles")
		file_list_len = len(self.file_list)
		first_idx = self.file_index / self.tiles * self.tiles
		last_idx = first_idx + self.tiles

		#print("MDC: Tiles: paintTiles: first_idx: %s, last_idx: %s" % (first_idx, last_idx))
		for idx in range(first_idx, last_idx):
			tile_pos = idx % self.tiles
			if file_list_len and idx < file_list_len:
				self.paintTile(idx, tile_pos)
			else:
				self.hideTile(tile_pos)

		tile_pos = self.file_index % self.tiles
		#print("MDC: Tiles: paintTiles: tile_pos: %s, last_tile_pos: %s" % (tile_pos, self.last_tile_pos))
		self.unselectTile(self.last_tile_pos)
		self.selectTile(tile_pos)
		self.showInfo(is_mounted)

	def showInfo(self, is_mounted=True):
		if self.file_list:
			x = self.file_list[self.file_index]
			path = x[FILE_PATH]
			filetype = _("File") if x[FILE_TYPE] == TYPE_FILE else _("Path")
		else:
			path = self.current_path
			filetype = _("Path")

		page = self.file_index / self.tiles + 1
		pages = len(self.file_list) / self.tiles + 1
		pages = pages if len(self.file_list) % self.tiles else pages - 1
		mounted = "" if is_mounted else "(" + _("not mounted") + ")"
		self.displayLCD("%d/%d" % (self.file_index + 1, len(self.file_list)), os.path.basename(path))
		self.displayOSD("%s: %d/%d - %s: %s %s" % (_("Page"), page, pages, filetype, path, mounted))

### Cursor moves

	def moveHome(self):
		if not self.busy:
			self.file_index = 0
			self.paintTiles()

	def moveLeft(self):
		if not self.busy:
			self.file_index -= 1
			if self.file_index < 0:
				self.file_index = len(self.file_list) - 1
			self.paintTiles()

	def moveRight(self):
		if not self.busy:
			self.file_index += 1
			if self.file_index > len(self.file_list) - 1:
				self.file_index = 0
			self.paintTiles()

	def moveUp(self):
		if not self.busy:
			self.file_index -= self.tile_columns
			if self.file_index < 0:
				self.file_index = len(self.file_list) - 1
			self.paintTiles()

	def moveDown(self):
		if not self.busy:
			self.file_index += self.tile_columns
			if self.file_index > len(self.file_list) - 1:
				self.file_index = 0
			self.paintTiles()

	def nextPage(self):
		if not self.busy:
			self.file_index += self.tiles
			self.file_index = self.file_index / self.tiles * self.tiles
			if self.file_index > len(self.file_list) - 1:
				self.file_index = 0
			self.paintTiles()

	def prevPage(self):
		if not self.busy:
			self.file_index -= self.tiles
			if self.file_index < 0:
				self.file_index = len(self.file_list) - 1
			self.file_index = self.file_index / self.tiles * self.tiles
			self.paintTiles()
