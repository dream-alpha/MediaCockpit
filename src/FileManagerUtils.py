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


from .__init__ import _


# file manager ops
FILE_OP_NONE = 0
FILE_OP_DELETE = 1
FILE_OP_MOVE = 2
FILE_OP_COPY = 3
FILE_OP_LOAD = 4  # loadDatabaseCache
FILE_OP_FSTRIM = 5  # execute fstrim command

FILE_TASK = _("File Task")
file_op_msg = {
    FILE_OP_NONE: _("None"),
    FILE_OP_LOAD: _("Loading"),
    FILE_OP_DELETE: _("Deleting"),
    FILE_OP_MOVE: _("Moving"),
    FILE_OP_COPY: _("Copying"),
    FILE_OP_FSTRIM: _("FSTrim"),
}

# file manager errors
FILE_OP_ERROR_NONE = 0
FILE_OP_ERROR_NO_DISKSPACE = 1
FILE_OP_ERROR_ABORT = 2
FILE_OP_ERROR = 100

# database file
SQL_DB_MVC = "moviecockpit.db"
SQL_DB_MDC = "mediacockpit.db"

# file types
FILE_TYPE_FILE = 1
FILE_TYPE_DIR = 2
FILE_TYPE_LINK = 3

# recordings indexes
FILE_IDX_TYPE = 0
FILE_IDX_BOOKMARK = 1
FILE_IDX_PATH = 2
FILE_IDX_RELPATH = 3
FILE_IDX_DIR = 4
FILE_IDX_RELDIR = 5
FILE_IDX_FILENAME = 6
FILE_IDX_EXT = 7
FILE_IDX_NAME = 8
FILE_IDX_EVENT_START_TIME = 9
FILE_IDX_RECORDING_START_TIME = 10
FILE_IDX_RECORDING_STOP_TIME = 11
FILE_IDX_LENGTH = 12
FILE_IDX_DESCRIPTION = 13
FILE_IDX_EXTENDED_DESCRIPTION = 14
FILE_IDX_SERVICE_REFERENCE = 15
FILE_IDX_SIZE = 16
FILE_IDX_CUTS = 17
FILE_IDX_SORT = 18
FILE_IDX_HOSTNAME = 19

# file types
MDC_TYPE_FILE = 1
MDC_TYPE_DIR = 2
MDC_TYPE_LINK = 3

# media indexes
MDC_IDX_TYPE = 0
MDC_IDX_BOOKMARK = 1
MDC_IDX_PATH = 2
MDC_IDX_RELPATH = 3
MDC_IDX_DIR = 4
MDC_IDX_RELDIR = 5
MDC_IDX_FILENAME = 6
MDC_IDX_EXT = 7
MDC_IDX_NAME = 8
MDC_IDX_DATE = 9
MDC_IDX_MEDIA = 10
MDC_IDX_META = 11

# media types
MDC_MEDIA_TYPE_UP = 0
MDC_MEDIA_TYPE_DIR = 1
MDC_MEDIA_TYPE_PLAYLIST = 2
MDC_MEDIA_TYPE_PICTURE = 3
MDC_MEDIA_TYPE_MOVIE = 4
MDC_MEDIA_TYPE_MUSIC = 5
MDC_MEDIA_TYPE_FILE = [MDC_MEDIA_TYPE_PICTURE, MDC_MEDIA_TYPE_MOVIE, MDC_MEDIA_TYPE_MUSIC]

# covers indexes
COVER_IDX_PATH = 0
COVER_IDX_COVER = 1
