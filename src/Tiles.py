#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2024 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# For more information on the GNU General Public License see:
# <http://www.gnu.org/licenses/>.


import os
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import config
from Screens.Screen import Screen
from enigma import eSize, ePoint, gFont
from skin import parseColor
from Tools.LoadPixmap import LoadPixmap
from .SkinUtils import getSkinPath, getSkinName
from .Debug import logger
from .__init__ import _
from .FileListUtils import FILE_IDX_TYPE, FILE_IDX_PATH
from .FileListUtils import FILE_TYPE_FILE, FILE_TYPE_UP, FILE_TYPE_DIR, FILE_TYPE_PLAYLIST, FILE_TYPE_PICTURE, FILE_TYPE_MOVIE, FILE_TYPE_MUSIC
from .MediaCockpitSummary import MediaCockpitSummary


class Tiles(Screen):

	def __init__(self, csel, session):
		self.csel = csel
		Screen.__init__(self, session)
		self.skinName = getSkinName(self.__class__.__name__)
		self.tile_columns = 5
		self.tile_rows = 3
		self.file_list = []
		self.current_dir = None
		self.tiles = self.tile_columns * self.tile_rows

		self.selection_size_offset = config.plugins.mediacockpit.selection_size_offset.value
		self.selection_font_offset = config.plugins.mediacockpit.selection_font_offset.value
		self.normal_background_color = parseColor(config.plugins.mediacockpit.normal_background_color.value)
		self.selection_background_color = parseColor(config.plugins.mediacockpit.selection_background_color.value)
		self.normal_foreground_color = parseColor(config.plugins.mediacockpit.normal_foreground_color.value)
		self.selection_foreground_color = parseColor(config.plugins.mediacockpit.selection_foreground_color.value)
		self.selection_frame_color = parseColor(config.plugins.mediacockpit.selection_frame_color.value)

		for tile_pos in range(self.tiles):
			self.csel["Frame%d" % tile_pos] = Label()
			self.csel["Frame%d" % tile_pos].hide()
			self.csel["Tile%d" % tile_pos] = Label()
			self.csel["Tile%d" % tile_pos].hide()
			self.csel["Picture%d" % tile_pos] = Pixmap()
			self.csel["Icon%d" % tile_pos] = Pixmap()
			self.csel["Text%d" % tile_pos] = Label()

		self.icons = {}
		self.busy = False
		self.last_tile_pos = -1
		self.onShow.append(self.initTileAttribs)

	def initTileAttribs(self):
		logger.debug("...")
		self.icons = {}
		self.icon_size = self.csel["Icon0"].instance.size()
		self.icons[FILE_TYPE_PICTURE] = LoadPixmap(getSkinPath("images/" + "picture.svg"), cached=True, size=self.icon_size)
		self.icons[FILE_TYPE_MOVIE] = LoadPixmap(getSkinPath("images/" + "movie.svg"), cached=True, size=self.icon_size)
		self.icons[FILE_TYPE_MUSIC] = LoadPixmap(getSkinPath("images/" + "music.svg"), cached=True, size=self.icon_size)
		self.icons[FILE_TYPE_DIR] = LoadPixmap(getSkinPath("images/" + "folder.svg"), cached=True, size=self.icon_size)
		self.icons[FILE_TYPE_PLAYLIST] = LoadPixmap(getSkinPath("images/" + "playlist.svg"), cached=True, size=self.icon_size)
		self.icons[FILE_TYPE_UP] = LoadPixmap(getSkinPath("images/" + "dirup.svg"), cached=True, size=self.icon_size)

		self.thumbnail_size = self.csel["Picture0"].instance.size()
		config.plugins.mediacockpit.thumbnail_size_width.value = self.thumbnail_size.width()
		config.plugins.mediacockpit.thumbnail_size_width.save()
		config.plugins.mediacockpit.thumbnail_size_height.value = self.thumbnail_size.height()
		config.plugins.mediacockpit.thumbnail_size_height.save()

		for tile_pos in range(self.tiles):
			for tile_element in ["Tile%d", "Text%d"]:
				self.csel[tile_element % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
				self.csel[tile_element % tile_pos].instance.setBackgroundColor(self.normal_background_color)
			self.csel["Frame%d" % tile_pos].instance.setBackgroundColor(self.selection_frame_color)

		font = self.csel["Text0"].instance.getFont()
		self.font_family = font.family
		self.font_size = font.pointSize

	def selectTile(self, tile_pos):
		logger.debug("tile_pos: %s, last_tile_pos: %s", tile_pos, self.last_tile_pos)
		if self.file_list and self.last_tile_pos < 0 and tile_pos >= 0:  # pylint: disable=R1716
			if config.plugins.mediacockpit.frame.value:
				self.csel["Frame%d" % tile_pos].show()
			for tile_element in ["Frame%d", "Tile%d", "Picture%d", "Icon%d", "Text%d"]:
				size = self.csel[tile_element % tile_pos].instance.size()
				pos = self.csel[tile_element % tile_pos].instance.position()
				self.csel[tile_element % tile_pos].instance.resize(eSize(size.width() + self.selection_size_offset * 2, size.height() + self.selection_size_offset * 2))
				self.csel[tile_element % tile_pos].instance.move(ePoint(pos.x() - self.selection_size_offset, pos.y() - self.selection_size_offset))
			for tile_element in ["Tile%d", "Text%d"]:
				self.csel[tile_element % tile_pos].instance.setBackgroundColor(self.selection_background_color)
				self.csel[tile_element % tile_pos].instance.setForegroundColor(self.selection_foreground_color)
			self.csel["Text%d" % tile_pos].instance.setFont(gFont(self.font_family, self.font_size + self.selection_font_offset))
			pos = self.csel["Text%d" % tile_pos].instance.position()
			self.csel["Text%s" % tile_pos].move(ePoint(pos.x(), pos.y() + self.selection_size_offset))
			self.last_tile_pos = tile_pos

	def unselectTile(self, tile_pos):
		logger.debug("tile_pos: %s, last_tile_pos: %s", tile_pos, self.last_tile_pos)
		if self.last_tile_pos > -1 and tile_pos >= 0:
			self.csel["Frame%d" % tile_pos].hide()
			for tile_element in ["Frame%d", "Tile%d", "Picture%d", "Icon%d", "Text%d"]:
				size = self.csel[tile_element % tile_pos].instance.size()
				pos = self.csel[tile_element % tile_pos].instance.position()
				self.csel[tile_element % tile_pos].instance.resize(eSize(size.width() - self.selection_size_offset * 2, size.height() - self.selection_size_offset * 2))
				self.csel[tile_element % tile_pos].instance.move(ePoint(pos.x() + self.selection_size_offset, pos.y() + self.selection_size_offset))
			for tile_element in ["Tile%d", "Text%d"]:
				self.csel[tile_element % tile_pos].instance.setBackgroundColor(self.normal_background_color)
				self.csel[tile_element % tile_pos].instance.setForegroundColor(self.normal_foreground_color)
			self.csel["Text%d" % tile_pos].instance.setFont(gFont(self.font_family, self.font_size))
			pos = self.csel["Text%d" % tile_pos].instance.position()
			self.csel["Text%s" % tile_pos].move(ePoint(pos.x(), pos.y() - self.selection_size_offset))
		self.last_tile_pos = -1

	def displayLCD(self, title, info):
		# logger.debug("title: %s, info: %s", title, info)
		self["lcd_title"].setText(title)
		self["lcd_info"].setText(info)

	def displayOSD(self, info):
		# logger.debug("info: %s", info)
		self["osd_info"].setText(_("MediaCockpit") + " - " + info)

	def hideTile(self, tile_pos):
		for tile_element in ["Frame%d", "Tile%d", "Picture%d", "Icon%d", "Text%d"]:
			self.csel[tile_element % tile_pos].hide()

	def hideTiles(self):
		self.unselectTile(self.last_tile_pos)
		for tile_pos in range(self.tiles):
			self.hideTile(tile_pos)

	def paintTile(self, idx, tile_pos):
		logger.debug("idx: %s, tile_pos: %s", idx, tile_pos)
		path, atype, _date, _meta = self.file_list[idx]
		logger.debug("path: %s", path)
		self.csel["Tile%d" % tile_pos].show()
		if atype == FILE_TYPE_UP:
			self.csel["Text%d" % tile_pos].setText("..")
		else:
			self.csel["Text%d" % tile_pos].setText(os.path.basename(path))
		thumbnail_path = None
		if atype != FILE_TYPE_UP:
			filename, ext = os.path.splitext(path)
			for thumbnail in [filename + ".thumbnail" + ext, filename + ".thumbnail.jpg"]:
				if os.path.exists(thumbnail):
					thumbnail_path = thumbnail
					break
		if thumbnail_path:
			self.csel["Picture%d" % tile_pos].instance.setPixmap(LoadPixmap(thumbnail_path, cached=False))
			self.csel["Icon%d" % tile_pos].hide()
			self.csel["Text%d" % tile_pos].hide()
			self.csel["Picture%d" % tile_pos].show()
		else:
			self.csel["Picture%d" % tile_pos].hide()
			self.csel["Icon%d" % tile_pos].instance.setPixmap(self.icons[atype])
			self.csel["Icon%d" % tile_pos].show()
			self.csel["Text%d" % tile_pos].show()

	def paintTiles(self, is_mounted=True):
		logger.info("file_index: %s, len(file_list): %s", self.file_index, len(self.file_list))
		file_list_len = len(self.file_list)
		first_idx = self.file_index / self.tiles * self.tiles
		last_idx = first_idx + self.tiles

		logger.debug("first_idx: %s, last_idx: %s", first_idx, last_idx)
		for idx in range(first_idx, last_idx):
			tile_pos = idx % self.tiles
			if file_list_len and idx < file_list_len:
				self.paintTile(idx, tile_pos)
			else:
				self.hideTile(tile_pos)

		tile_pos = self.file_index % self.tiles
		logger.debug("tile_pos: %s, last_tile_pos: %s", tile_pos, self.last_tile_pos)
		self.unselectTile(self.last_tile_pos)
		self.selectTile(tile_pos)
		self.showInfo(is_mounted)

	def showInfo(self, is_mounted=True):
		if self.file_list:
			afile = self.file_list[self.file_index]
			path = afile[FILE_IDX_PATH]
			filetype = _("File") if afile[FILE_IDX_TYPE] in FILE_TYPE_FILE else _("Path")
		else:
			path = self.current_dir
			filetype = _("Path")
		logger.debug("path: %s", path)
		page = self.file_index / self.tiles + 1
		pages = len(self.file_list) / self.tiles + 1
		pages = pages if len(self.file_list) % self.tiles else pages - 1
		mounted = "" if is_mounted else "(" + _("not mounted") + ")"
		self.displayLCD("%d/%d" % (self.file_index + 1, len(self.file_list)), os.path.basename(path))
		self.displayOSD("%s: %d/%d - %s: %s %s" % (_("Page"), page, pages, filetype, path, mounted))

# cursor moves

	def moveTop(self):
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

	def createSummary(self):
		return MediaCockpitSummary
