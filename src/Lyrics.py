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


from __init__ import _
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from xml.etree.cElementTree import fromstring
from urllib import quote
from Components.ScrollLabel import ScrollLabel
from mutagen.id3 import ID3
from HttpUtils import sendUrlCommand
from EncodingUtils import getEncodedString


class Lyrics(Screen):

	IS_DIALOG = True

	def __init__(self, session, currentsong):
		self.session = session
		Screen.__init__(self, session)
		self.skinName = [self.__class__.__name__]
		self["resulttext"] = Label()
		self["actions"] = ActionMap(["WizardActions", "DirectionActions"],
		{
			"back": self.close,
			"upUp": self.pageUp,
			"leftUp": self.pageUp,
			"downUp": self.pageDown,
			"rightUp": self.pageDown,
		}, -1)
		self["lyric_text"] = ScrollLabel()
		self.current_song = currentsong
		self.onLayoutFinish.append(self.startRun)

	def startRun(self):
		self.setTitle(_("Lyrics"))
		# get lyric-text from id3 tag
		try:
			audio = ID3(self.current_song.filename)
		except Exception:
			audio = None
		text = getEncodedString(self.getLyricsFromID3Tag(audio)).replace("\r\n", "\n")
		text = text.replace("\r", "\n")
		#print("MDC: Lyrics: startRun: text: %s" % text)
		self["lyric_text"].setText(text)

	def getLyricsFromID3Tag(self, tag):
		if tag:
			for frame in tag.values():
				if frame.FrameID == "USLT":
					return frame.text
		url = "http://api.chartlyrics.com/apiv1.asmx/SearchLyricDirect?artist=%s&song=%s" % (quote(self.current_song.artist), quote(self.current_song.title))
		#print("MDC: Lyrics: getLyricsfrom ID3Tag: url: = %s" % url)
		sendUrlCommand(url, None, 10).addCallback(self.gotLyrics).addErrback(self.urlError)
		return _("No lyrics found in id3-tag, trying api.chartlyrics.com...")

	def urlError(self, error=None):
		if error is not None:
			self["lyric_text"].setText(str(error.getErrorMessage()))

	def gotLyrics(self, xmlstring):
		#print("MDC: Lyrics: gotLyrics: xmlstring: %s" % xmlstring)
		root = fromstring(xmlstring)
		lyrictext = root.findtext("{http://api.chartlyrics.com/}Lyric").encode("utf-8", 'ignore')
		#print("MDC: Lyrics: gotLyrics: lyrictxt: %s" % lyrictext)
		self["lyric_text"].setText(lyrictext)
		title = root.findtext("{http://api.chartlyrics.com/}LyricSong").encode("utf-8", 'ignore')
		print("MDC-I: Lyrics: gotLyrics: title: %s" % title)
		artist = root.findtext("{http://api.chartlyrics.com/}LyricArtist").encode("utf-8", 'ignore')
		print("MDC-I: Lyrics: gotLyrics: artist: %s" % artist)
		result = "%s (%s)" % (self.current_song.title, self.current_song.artist)
		self["resulttext"].setText(result)
		if not lyrictext:
			self["lyric_text"].setText(_("No lyrics found"))

	def pageUp(self):
		self["lyric_text"].pageUp()

	def pageDown(self):
		self["lyric_text"].pageDown()
