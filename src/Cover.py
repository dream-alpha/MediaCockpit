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
from twisted.web.client import downloadPage
from twisted.web.client import getPage
from Tools.BoundFunction import boundFunction
from FileUtils import createDirectory


class Cover():

	def __init__(self, download_dir, coverDownloadFinished, coverDownloadFailed):
		#print("MDC: Cover: __init__: download_dir: %s" % download_dir)
		self.download_dir = download_dir
		self.coverDownloadFinished = coverDownloadFinished
		self.coverDownloadFailed = coverDownloadFailed
		if not os.path.exists(self.download_dir):
			rc = createDirectory(self.download_dir)
			if rc:
				self.download_dir = "/tmp"

	def determineContentURL(self, artist, album, title):
		print("MDC-E: Cover: determineContentURL: overridden in child class: artist: %s, album: %s, title: %s" % (artist, album, title))

	def determineCoverURL(self, result):
		print("MDC-E: Cover: determineCoverURL: overridden in child class: result" % result)

	def determinePath(self, artist, album, title):
		#print("MDC: Cover: determinePath: artist: %s, album: %s, title: %s" % (artist, album, title))
		if artist and album:
			path = os.path.join(self.download_dir, "%s_%s" % (self.formatFilename(artist), self.formatFilename(album)))
		else:
			path = os.path.join(self.download_dir, self.formatFilename(title))
		return path

	def getCover(self, artist, album, title):
		#print("MDC: Cover: getCover: artist: %s, album: %s, title: %s" % (artist, album, title))
		path = self.determinePath(artist, album, title)
		if os.path.exists(path):
			self.coverDownloadFinished(path, None)
		else:
			url = self.determineContentURL(artist, album, title)
			if url:
				getPage(url, timeout=4, agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17').addCallback(boundFunction(self.getCoverCallback, path)).addErrback(self.coverDownloadFailed)

	def getCoverCallback(self, filename, result):
		#print("MDC: Cover: determineCoverCallback: filename: %s, result: %s" % (filename, result))
		url = self.determineCoverURL(result)
		if url:
			#print("MDC: Cover: getCoverCallback: downloading cover from %s to %s" % (url, filename))
			downloadPage(url, filename).addCallback(boundFunction(self.coverDownloadFinished, filename)).addErrback(self.coverDownloadFailed)
		else:
			print("MDC-E: Cover: getCoverCallback: no cover found")
			self.coverDownloadFailed(None)

	def formatFilename(self, filename):
		f = "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' '])
		return f.replace(" ", "_")
