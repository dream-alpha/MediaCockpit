#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2019 by dream-alpha
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
from enigma import eServiceReference

# DVB types
sidDVB = eServiceReference.idDVB	# eServiceFactoryDVB::id  enum {id = 0x1};
sidDVD = eServiceReference.idDVD	# eServiceFactoryDVD::id  enum {id = 0x1111};
sidM2TS = eServiceReference.idM2TS	# eServiceFactoryM2TS::id enum {id = 0x3};
sidDefault = eServiceReference.idGST	# eServiceFactoryGST::id  enum {id = 0x1001};

# ext types
extTS = frozenset([".ts", ".trp"])
extMP3 = frozenset([".mp3"])
extM2ts = frozenset([".m2ts"])
extIfo = frozenset([".ifo"])
extIso = frozenset([".iso", ".img"])
extDvd = extIfo | extIso
extBlu = frozenset([".bdmv"])

# all media ext types
extVideo = [".avi", ".ts", ".trp", ".divx", ".f4v", ".img", ".ifo", ".iso", ".m4v", ".mkv", ".mov", ".mp4", ".mpeg", ".mpg", ".mts", ".vob", ".wmv", ".bdmv", ".asf", ".stream", ".webm"]
extPicture = [".jpg", ".jpeg", ".png"]
extMusic = [".mp3"]
extPlaylist = [".m3u"]
extMedia = extVideo + extPicture + extPlaylist


def getService(path, name=""):
	print("MCD: ServiceUtils: getService: path: %s" % path)
	ext = os.path.splitext(path)[1].lower()
	service = None
	if path:
		if ext in extTS:
			service = eServiceReference(sidDVB, 0, path)
		elif ext in extDvd:
			service = eServiceReference(sidDVD, 0, path)
		elif ext in extM2ts:
			service = eServiceReference(sidM2TS, 0, path)
		else:
			service = eServiceReference(sidDefault, 0, path)
			DEFAULT_VIDEO_PID = 0x44
			service.setData(0, DEFAULT_VIDEO_PID)
			DEFAULT_AUDIO_PID = 0x45
			service.setData(1, DEFAULT_AUDIO_PID)
		if name:
			service.setName(name)
	return service
