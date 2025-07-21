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
from pipes import quote
import glob
from .Debug import logger


def stripCutNumber(path):
    filename, ext = os.path.splitext(path)
    if len(filename) > 3:
        if filename[-4] == "_" and filename[-3:].isdigit():
            filename = filename[:-4]
        path = filename + ext
    return path


def readFile(path):
    data = ""
    try:
        with open(path, "r") as f:
            data = f.read()
    except Exception as e:
        logger.info("path: %s, exception: %s", path, e)
    return data


def writeFile(path, data):
    try:
        with open(path, "w") as f:
            f.write(data)
    except Exception as e:
        logger.error("path: %s, exception: %s", path, e)


def deleteFile(path):
    os.popen("rm %s" % quote(path)).read()


def deleteFiles(path, clear=False):
    for afile in glob.glob(path):
        if clear:
            writeFile(afile, "")
        deleteFile(afile)


def touchFile(path):
    os.popen("touch %s" % quote(path)).read()


def copyFile(src_path, dest_path):
    os.popen("cp %s %s" % (quote(src_path), quote(dest_path))).read()


def renameFile(src_path, dest_path):
    os.popen("mv %s %s" % (quote(src_path), quote(dest_path))).read()


def createDirectory(path):
    os.popen("mkdir -p %s" % quote(path)).read()


def createSymlink(src, dst):
    logger.info("link: src: %s > %s", src, dst)
    os.symlink(src, dst)


def deleteDirectory(path):
    os.popen("rm -rf %s" % quote(path)).read()
