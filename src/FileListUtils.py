#!/usr/bin/python
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
import json
from six import text_type
from Components.config import config
from Plugins.SystemPlugins.CacheCockpit.FileManager import FileManager
from .Debug import logger
from .FileManagerUtils import MDC_TYPE_DIR
from .FileManagerUtils import MDC_IDX_TYPE, MDC_IDX_PATH, MDC_IDX_MEDIA, MDC_IDX_META, MDC_IDX_DATE
from .FileManagerUtils import MDC_MEDIA_TYPE_FILE, MDC_MEDIA_TYPE_PICTURE, MDC_MEDIA_TYPE_MUSIC, MDC_MEDIA_TYPE_DIR, MDC_MEDIA_TYPE_UP
from .ConfigInit import sort_modes
from .Version import ID
from .FileUtils import readFile


def nextIndex(file_index, file_list_length):
    index = -1
    if file_list_length > 0:
        index = (file_index + 1) % file_list_length
    return index


def previousIndex(file_index, file_list_length):
    index = -1
    if file_list_length > 0:
        index = file_index - 1 if file_index else file_list_length - 1
    return index


def getIndex(file_list, path):
    file_index = 0 if file_list else -1
    for i, afile in enumerate(file_list):
        if afile[MDC_IDX_PATH] == path:
            file_index = i
            break
    return file_index


def getPath(file_list, index):
    current_path = ""
    if file_list:
        afile = file_list[index]
        current_path = afile[MDC_IDX_PATH]
    logger.debug("current_path: %s", current_path)
    return current_path


def getDir(file_list, index):
    current_dir = ""
    if file_list:
        afile = file_list[index]
        logger.debug("afile: %s", afile)
        path = afile[MDC_IDX_PATH]
        if afile[MDC_IDX_TYPE] == MDC_TYPE_DIR and not path.endswith(".."):
            current_dir = path
        else:
            current_dir = os.path.dirname(path)
    logger.debug("current_dir: %s", current_dir)
    return current_dir


def getFile(file_list, value):
    afile = []
    if file_list:
        if isinstance(value, int):
            afile = file_list[value]
        elif isinstance(value, text_type):
            afile = file_list[getIndex(file_list, value)]
    return afile


def splitMediaSongList(file_list):
    song_list = []
    media_list = []
    for afile in file_list:
        logger.debug("afile: %s", afile)
        if afile[MDC_IDX_MEDIA] in MDC_MEDIA_TYPE_FILE:
            if afile[MDC_IDX_MEDIA] == MDC_MEDIA_TYPE_MUSIC:
                song_list.append(afile)
            else:
                media_list.append(afile)
    return media_list, song_list


def sortList(file_list):
    file_list_sort = config.plugins.mediacockpit.sort.value
    sort_across_dirs = config.plugins.mediacockpit.sort_across_dirs.value
    mode, order = sort_modes[file_list_sort][0]
    logger.debug("sort_mode: %s, sort_order: %s", mode, order)

    if mode == "alpha":
        if sort_across_dirs:
            if order:
                file_list.sort(key=lambda afile: (min(afile[MDC_IDX_MEDIA], MDC_MEDIA_TYPE_PICTURE), os.path.basename(
                    afile[MDC_IDX_PATH]).lower()), reverse=True)
            else:
                file_list.sort(key=lambda afile: (min(
                    afile[MDC_IDX_MEDIA], MDC_MEDIA_TYPE_PICTURE), os.path.basename(afile[MDC_IDX_PATH]).lower()))
        else:
            if order:
                file_list.sort(key=lambda afile: (min(
                    afile[MDC_IDX_MEDIA], MDC_MEDIA_TYPE_PICTURE), afile[MDC_IDX_PATH].lower()), reverse=True)
            else:
                file_list.sort(key=lambda afile: (
                    min(afile[MDC_IDX_MEDIA], MDC_MEDIA_TYPE_PICTURE), afile[MDC_IDX_PATH].lower()))
    elif mode == "date":
        if order:
            file_list.sort(key=lambda afile: (min(
                afile[MDC_IDX_MEDIA], MDC_MEDIA_TYPE_PICTURE), afile[MDC_IDX_DATE]), reverse=True)
        else:
            file_list.sort(key=lambda afile: (
                min(afile[MDC_IDX_MEDIA], MDC_MEDIA_TYPE_PICTURE), afile[MDC_IDX_DATE]))
    return file_list


def scanPlaylistFiles(path):
    logger.debug("path: %s", path)
    file_list = []
    playlist_dir = os.path.dirname(path)
    lines = readFile(path).splitlines()
    for line in lines:
        if line and not line.startswith("#"):
            logger.debug("line: %s", line)
            path = line
            if not path.startswith("/"):
                path = os.path.join(playlist_dir, path)
            file_list.append(path)
    return file_list


def createBookmarkEntries(bookmarks):
    logger.debug("bookmarks: %s", bookmarks)
    alist = []
    meta = {}
    for bookmark in bookmarks:
        afile = list(FileManager.getInstance(
            ID).newDirData(bookmark, MDC_TYPE_DIR))
        logger.debug("afile: %s", afile)
        afile[MDC_IDX_MEDIA] = MDC_MEDIA_TYPE_DIR
        afile[MDC_IDX_META] = json.dumps(meta)
        alist.append(afile)
    return alist


def createParentDirEntry(path):
    logger.debug("path: %s", path)
    meta = {}
    if os.path.splitext(path)[1] != ".m3u":
        path = os.path.join(path, "..")
    afile = list(FileManager.getInstance(ID).newDirData(path, MDC_TYPE_DIR))
    afile[MDC_IDX_MEDIA] = MDC_MEDIA_TYPE_UP
    afile[MDC_IDX_META] = json.dumps(meta)
    logger.debug("afile: %s", afile)
    return afile
