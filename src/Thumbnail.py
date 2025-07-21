# encoding: utf-8
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


from enigma import eSize
from Components.config import config
from .PictureUtils import createThumbnail


class Thumbnail():

    def __init__(self):
        self.thumbnail_size = eSize(
            int(config.plugins.mediacockpit.thumbnail_size_width.value),
            int(config.plugins.mediacockpit.thumbnail_size_height.value)
        )

    def createThumbnail(self, path, create=False):
        createThumbnail(path, self.thumbnail_size, create)
