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
import pexif
from PIL import Image
from PIL import ImageFile
from PIL.ExifTags import TAGS
ImageFile.LOAD_TRUNCATED_IMAGES = True


def getExifData(path):
	#print("MDC: PictureUtils: getExifData: path: %s" % path)
	exif_data = {}
	exif = {}
	width = 0
	height = 0
	try:
		img = Image.open(path)
		width, height = img.size
		exif_data = img._getexif()
	except Exception as e:
		print("MDC-E: PictureUtils: getExifData: exception: %s" % e)
	#print("MDC: PictureUtils: getExifData: exif_data: %s" % str(exif_data))
	if exif_data:
		for key, value in exif_data.iteritems():
			if key in TAGS:
				tag = TAGS[key]
				if tag != "UserComment" and tag != "MakerNote":
					exif[tag] = value
	if "ExifImageWidth" not in exif and width:
		exif["ExifImageWidth"] = width
	if "ExifImageHeight" not in exif and height:
		exif["ExifImageHeight"] = height
	if "Orientation" not in exif:
		exif["Orientation"] = 1
	#print("MDC: PictureUtils: getExifData: exif: %s" % str(exif))
	return exif


def setExifOrientation(path, orientation):
	#print("MDC: PictureUtils: setExifOrientation: path: %s, orientation: %s" % (path, orientation))
	_filename, ext = os.path.splitext(path)
	if ext.lower() == ".jpg":
		try:
			img = pexif.JpegFile.fromFile(path)
			img.exif.primary.Orientation = [orientation]
			img.writeFile(path)
		except Exception as e:
			print("MDC-E: PictureUtils: setExifOriention: path: %s, exception: %s" % (path, e))


def rotatePicture(in_path, out_path, degrees):
	try:
		img = Image.open(in_path)
		if img:
			tmpimg = img.rotate(degrees, resample=Image.NEAREST, expand=True)
			tmpimg.save(out_path)
	except Exception as e:
		print("MDC-E: PictureUtils: rotatePicture: in_path: %s, exception: %s" % (in_path, e))
		return False
	return True


def transformPicture(path, orientation):
	#print("MDC: PictureUtils: transformPicture: path: %s, orientation: %s" % (path, orientation))
	filename, ext = os.path.splitext(path)
	output_file = filename + ".transformed" + ext
	try:
		img = Image.open(path)
		if img:
			if orientation == 8:
				rotatePicture(path, output_file, 90)
			if orientation == 6:
				rotatePicture(path, output_file, -90)
			if orientation == 3:
				rotatePicture(path, output_file, -180)
			if orientation in [3, 6, 8]:
				setExifOrientation(output_file, 1)
	except Exception as e:
		print("MDC-E: PictureUtils: transformPicture: path: %s, e: %s" % (path, e))


def createThumbnail(path, size, create=False):
	#print("MDC: PictureUtils: createThumbnail: path: %s, size: %s" % (path, str(size)))
	filename, ext = os.path.splitext(path)
	thumbnail_path = filename + ".thumbnail" + ext
	if not os.path.exists(thumbnail_path) or create:
		print("MDC-I: PictureUtils: createThumbnail: creating %s" % thumbnail_path)
		input_path = filename + ".transformed" + ext
		if not os.path.exists(input_path):
			input_path = path
		width, height = size
		side = max(width, height)
		try:
			img = Image.open(input_path)
			img.thumbnail((side, side))
			img.save(thumbnail_path)
		except Exception as e:
			print("MDC-E: PictureUtils: createThumbnail: path: %s, exception: %s" % (path, e))
