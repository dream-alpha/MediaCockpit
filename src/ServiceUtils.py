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
from enigma import eServiceReference, loadPNG
from Components.config import config
from .Debug import logger


SID_DVB = eServiceReference.idDVB	  # eServiceFactoryDVB::id  enum{id = 0x0001};
SID_DVD = eServiceReference.idDVD	  # eServiceFactoryDVD::id  enum{id = 0x1111};
SID_M2TS = eServiceReference.idM2TS	  # eServiceFactoryM2TS::id enum{id = 0x0003};
SID_GST = eServiceReference.idGST	  # eServiceFactoryGST::id  enum{id = 0x1001};


EXT_TS = [".ts", ".trp"]
EXT_M2TS = [".m2ts"]
EXT_DVD = [".ifo", ".iso", ".img"]
EXT_VIDEO = [".avi", ".divx", ".f4v", ".flv", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".mts", ".vob", ".wmv", ".asf", ".stream", ".webm"]
EXT_BLU = [".bdmv"]

EXT_PICTURE = [".jpg", ".jpeg", ".png"]
EXT_MUSIC = [".mp3", ".wma"]
EXT_PLAYLIST = [".m3u"]

ALL_VIDEO = EXT_TS + EXT_M2TS + EXT_DVD + EXT_VIDEO + EXT_BLU
ALL_MEDIA = ALL_VIDEO + EXT_PICTURE + EXT_MUSIC + EXT_PLAYLIST


# DEFAULT_VIDEO_PID = 0x44
# DEFAULT_AUDIO_PID = 0x45


def getService(path, name=""):
    service = None
    ext = os.path.splitext(path)[1].lower()
    if ext in EXT_TS:
        service = eServiceReference(SID_DVB, 0, path)
    elif ext in EXT_DVD:
        service = eServiceReference(SID_DVD, 0, path)
    elif ext in EXT_M2TS:
        service = eServiceReference(SID_M2TS, 0, path)
    else:
        service = eServiceReference(SID_GST, 0, path)
        # service.setData(0, DEFAULT_VIDEO_PID)
        # service.setData(1, DEFAULT_AUDIO_PID)
    service.setName(name)
    return service


def getPiconPath(service_reference):
    pos = service_reference.rfind(':')
    if pos != -1:
        service_reference = service_reference[:pos].rstrip(':').replace(':', '_')
    picon_path = os.path.join(config.usage.configselection_piconspath.value, service_reference + '.png')
    logger.debug("picon_path: %s", picon_path)
    return picon_path


def getPicon(service_reference):
    return loadPNG(getPiconPath(service_reference))
