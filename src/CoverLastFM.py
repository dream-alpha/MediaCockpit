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


import json
import urllib
from Cover import Cover


class CoverLastFM(Cover):
	def __init__(self, download_dir, coverDownloadFinished, coverDownloadFailed):
		self.LASTFM_API_KEY = "e32301e97cfe55db2129c2bba6d0ce3a"
		self.LASTFM_URL = "http://ws.audioscrobbler.com/2.0/"
		Cover.__init__(self, download_dir, coverDownloadFinished, coverDownloadFailed)

	def determineContentURL(self, artist, album, title):
		print("MDC-I: CoverLastFM: determineContentURL: artist: %s, album: %s, title: %s" % (artist, album, title))
		self.artist = artist.encode('utf8')
		self.album = album.encode('utf8')
		url = self.LASTFM_URL\
			+ "?method=album.search"\
			+ "&api_key=" + self.LASTFM_API_KEY\
			+ "&album=" + urllib.quote(self.album)\
			+ "&format=json"
		#print("MDC: CoverLastFM: determineContentURL: url: %s" % url)
		return url

	def determineCoverURL(self, result):
		url = ""
		root = json.loads(result)
		if "results" in root:
			for album in root["results"]["albummatches"]["album"]:
				#print(album["image"])
				print("\n####################################################\n")
				print("     >>> %s, %s" % (album["name"], album["artist"]))
				if self.artist in album["artist"]:
					for image in album["image"]:
						print("     %s, %s" % (image["#text"], image["size"]))
						if image["size"] == "extralarge":
							url = str(image["#text"])
							break
				if url:
					break
		elif "message" in root:
			print("MDC-E: CoverLastFM: searchAlbum: error: %s" % root["message"])
		#print("MDC: CoverLastFM: searchAlbum: url: %s" % url)
		return url
