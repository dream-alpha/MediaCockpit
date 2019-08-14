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
from PIL import Image
from PIL.ExifTags import TAGS


def getExifData(path):
	#print("MDC: PictureUtils: getExifData: path: %s" % path)
	exif_data = None
	width = 0
	height = 0
	try:
		img = Image.open(path)
		width, height = img.size
		if img and hasattr(img, "_getexif"):
			exif_data = img._getexif()
	except Exception as e:
		print("MDC-E: PictureUtils: getExifData: exception: %s" % e)
	exif = {}
	if exif_data is not None:
		for key, value in exif_data.iteritems():
			if key in TAGS:
				tag = TAGS[key]
				if tag != "UserComment" and tag != "MakerNote":
					exif[tag] = value
	elif width and height:
		exif["ExifImageWidth"] = width
		exif["ExifImageHeight"] = height
	#print("MDC: PictureUtils: getExifData: exif: %s" % str(exif))
	return exif


def scalePicture(path, new_size):
	new_width, new_height = new_size
	filename, ext = os.path.splitext(path)
	tmpfile = path
	try:
		img = Image.open(path)
		width, height = img.size
		if width < new_width and height < new_height:
			tmpfile = filename + ".scaled" + ext
			if not os.path.exists(tmpfile):
				print("MDC: PictureUtils: scalePicture: path: %s" % path)
				print("MDC: PictureUtils: scalePicture: width: %s, height: %s" % (width, height))
				scaling_factor = float(new_height) / float(height)
				new_size = (int(width * scaling_factor), int(height * scaling_factor))
				print("MDC: PictureUtils: scalePicture: new_size %s" % str(new_size))
				tmpimg = img.resize(new_size, resample=Image.ANTIALIAS)
				tmpimg.save(tmpfile)
	except Exception as e:
		print("MDC: PictureUtils: scalePicture: exception: %s" % e)
	return tmpfile


def rotatePicture(path, degrees):
	filename, ext = os.path.splitext(path)
	tmpfile = filename + ".rotated" + ext
	if os.path.exists(tmpfile):
		path = tmpfile
	img = Image.open(path)
	tmpimg = img.rotate(degrees, resample=Image.NEAREST)
	tmpimg.save(tmpfile)
	return tmpfile


def rotatePictureExif(path, exif_data):
	#print("MDC: PictureUtils: rotatePictureExif: path: %s, exif_data: %s" % (path, str(exif_data)))
	filename, ext = os.path.splitext(path)
	tmpfile = filename + ".rotated" + ext
	if not os.path.exists(tmpfile):
		tmpfile = path
		if exif_data is None:
			exif_data = getExifData(path)
		#print("MDC: PictureUtils: rotatePictureExif: exif_data: %s" % str(exif_data))
		if "Orientation" in exif_data:
			orientation = exif_data["Orientation"]
			if (not (orientation == 1 or orientation == 0)) and ext != ".svg":
				#print("MDC: PictureUtils: rotatePictureExif: pic needs to be rotated")
				tmpfile = filename + ".rotated" + ext
				img = Image.open(path)
				if img:
					if orientation == 8:
						tmpimg = img.rotate(90, resample=Image.NEAREST)
						tmpimg.save(tmpfile)
					if orientation == 6:
						tmpimg = img.rotate(-90, resample=Image.NEAREST)
						tmpimg.save(tmpfile)
					if orientation == 3:
						tmpimg = img.rotate(-180, resample=Image.NEAREST)
						tmpimg.save(tmpfile)
	#print("MDC: PictureUtils: rotatePictureExif: tmpfile: %s" % tmpfile)
	return tmpfile
