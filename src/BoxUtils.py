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
from Components.config import config
from .FileUtils import readFile


def dimmOSD(hide):
    dimm = config.av.osd_alpha.value if hide else 0
    if os.path.exists("/proc/stb/video/alpha"):
        device = "/proc/stb/video/alpha"
    else:  # dream one, dream two
        device = "/sys/devices/platform/meson-fb/graphics/fb0/osd_plane_alpha"
    with open(device, "w") as f:
        f.write("%s" % dimm)


def getBoxType():
    box_type = "dm9XX"
    if os.path.exists("/proc/stb/info/model"):
        box_type = readFile("/proc/stb/info/model")
        box_type = box_type.replace("\n", "")
        if box_type == "one":
            box_type = "dreamone"
        if box_type == "two":
            box_type = "dreamtwo"
        if box_type == "seven":
            box_type = "dreamseven"
    return box_type
