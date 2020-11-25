#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2020 by dream-alpha
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
from mutagen.flac import FLAC
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.easymp4 import EasyMP4
from mutagen.oggvorbis import OggVorbis
from mutagen.aiff import AIFF
from datetime import timedelta
from EncodingUtils import getEncodedString


def getID3Tags(filename):
	audio = None
	isFlac = False
	is_audio = True
	title = ""
	genre = ""
	artist = ""
	album = ""
	tracknr = -1
	track = None
	date = None
	length = ""
	bitrate = None
	try:
		if filename.lower().endswith(".mp3"):
			audio = MP3(filename, ID3=EasyID3)
		elif filename.lower().endswith(".flac"):
			audio = FLAC(filename)
			isFlac = True
		elif filename.lower().endswith(".m4a"):
			audio = EasyMP4(filename)
		elif filename.lower().endswith(".ogg"):
			audio = OggVorbis(filename)
		elif filename.lower().endswith(".aif") or filename.lower().endswith(".aiff"):
			audio = AIFF(filename)
		else:
			is_audio = False
	except Exception:
		is_audio = False

	if audio:
		title = getEncodedString(audio.get('title', [os.path.splitext(os.path.basename(filename))[0]])[0])
		try:
			# list index out of range workaround
			genre = getEncodedString(audio.get('genre', ['n/a'])[0])
		except Exception:
			genre = "n/a"
		artist = getEncodedString(audio.get('artist', ['n/a'])[0])
		album = getEncodedString(audio.get('album', ['n/a'])[0])
		try:
			tracknr = int(audio.get('tracknumber', ['-1'])[0].split("/")[0])
		except Exception:
			tracknr = -1
		track = getEncodedString(audio.get('tracknumber', ['n/a'])[0])
		date = getEncodedString(audio.get('date', ['n/a'])[0])
		try:
			length = str(timedelta(seconds=int(audio.info.length))).encode("utf-8", 'ignore')
		except Exception:
			length = -1
		if not isFlac:
			bitrate = audio.info.bitrate / 1000
		else:
			bitrate = None
	elif is_audio:
		title = os.path.splitext(os.path.basename(filename))[0]
		genre = "n/a"
		artist = "n/a"
		album = "n/a"
		tracknr = -1
		track = None
		date = None
		length = ""
		bitrate = None

	return audio, is_audio, title, genre, artist, album, tracknr, track, date, length, bitrate
