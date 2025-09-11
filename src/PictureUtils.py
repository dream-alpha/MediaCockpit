# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
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
from PIL import Image
from PIL import ImageFile
from PIL.ExifTags import TAGS
from .Debug import logger
from . import pexif


ImageFile.LOAD_TRUNCATED_IMAGES = True


def getPicturePath(path):
    filename, ext = os.path.splitext(path)
    path_transformed = filename + ".transformed" + ext
    return path_transformed if os.path.exists(path_transformed) else path


def getExifData(path):
    logger.debug("path: %s", path)
    exif_data = {}
    exif = {}
    width = 0
    height = 0
    try:
        img = Image.open(path)
        width, height = img.size
        exif_data = img._getexif()  # pylint: disable=W0212
    except Exception as e:
        logger.error("exception: %s", e)
    # logger.debug("exif_data: %s", str(exif_data))
    if exif_data:
        for key, value in list(exif_data.items()):
            if key in TAGS:
                tag = TAGS[key]
                if tag not in ["UserComment", "MakerNote"]:
                    exif[tag] = value
    if "ExifImageWidth" not in exif and width:
        exif["ExifImageWidth"] = width
    if "ExifImageHeight" not in exif and height:
        exif["ExifImageHeight"] = height
    if "Orientation" not in exif:
        exif["Orientation"] = 1
    logger.debug("exif: %s", str(exif))
    return exif


def setExifOrientation(path, orientation):
    logger.debug("path: %s, orientation: %s", path, orientation)
    ext = os.path.splitext(path)[1]
    if ext.lower() == ".jpg":
        try:
            img = pexif.JpegFile.fromFile(path)
            img.exif.primary.Orientation = [orientation]
            img.writeFile(path)
        except Exception as e:
            logger.error("path: %s, exception: %s", path, e)


def rotatePicture(in_path, out_path, degrees):
    try:
        img = Image.open(in_path)
        if img:
            tmpimg = img.rotate(degrees, resample=Image.NEAREST, expand=True)
            tmpimg.save(out_path)
    except Exception as e:
        logger.error("in_path: %s, exception: %s", in_path, e)
        return False
    return True


def transformPicture(path, orientation):
    logger.debug("path: %s, orientation: %s", path, orientation)
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
        logger.error("path: %s, e: %s", path, e)


def createThumbnail(path, size, create=False):
    logger.debug("path: %s, size: %s", path, str(size))
    filename, ext = os.path.splitext(path)
    thumbnail_path = filename + ".thumbnail" + ext
    if not os.path.exists(thumbnail_path) or create:
        logger.info("creating %s", thumbnail_path)
        input_path = filename + ".transformed" + ext
        if not os.path.exists(input_path):
            input_path = path
        width = size.width()
        height = size.height()
        side = max(width, height)
        try:
            img = Image.open(input_path)
            img.thumbnail((side, side))
            img.save(thumbnail_path)
        except Exception as e:
            logger.error("path: %s, exception: %s", path, e)
