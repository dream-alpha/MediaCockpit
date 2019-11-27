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
import re
from __init__ import _
from Screens.Screen import Screen
from Components.ActionMap import ActionMap
from Components.Label import Label
from enigma import eServiceReference, iPlayableService, iServiceInformation
from twisted.web.client import downloadPage
from twisted.web.client import getPage
from Screens.MessageBox import MessageBox
from urllib import quote
from Tools.Directories import fileExists
from Tools.LoadPixmap import LoadPixmap
from Components.Pixmap import Pixmap
from Components.Sources.MDCCurrentService import MDCCurrentService
from Screens.InfoBarGenerics import InfoBarSeek, InfoBarNotifications
from Components.ServiceEventTracker import ServiceEventTracker, InfoBarBase
from Tools.BoundFunction import boundFunction
from random import shuffle
from Components.config import config
from MetaFile import FILE_PATH
from ID3Tags import getID3Tags
from ServiceUtils import sidDefault
from SkinUtils import getSkinPath
from Components.MerlinMusicPlayerWidget import MerlinMusicPlayerWidget
from FileListUtils import previousIndex, nextIndex
from merlin_musicplayer.emerlinmusicplayer import eMerlinMusicPlayer
from KeyHelp import Help
try:
	import merlin_musicplayer._emerlinmusicplayer  # noqa: F401, pylint: disable=W0611
except Exception:
	pass


ENIGMA_MERLINPLAYER_ID = 0x1019


class MDCMusicPlayerSummary(Screen):

	def __init__(self, session, parent):
		Screen.__init__(self, session)
		self.skinName = [self.__class__.__name__]
		self["title"] = Label()
		self["Service"] = MDCCurrentService(session.nav, parent)

	def setText(self, text):
		self["title"].setText(text)

class MusicPlayerHelp(Help):
	def __init__(self, session):
		Help.__init__(self, session)

	def firstStart(self):
		alist = []
		alist.append((_("Exit"), LoadPixmap(getSkinPath("images/" + "key_red.png"), cached=False)))
		alist.append((_("Toggle shuffle"), LoadPixmap(getSkinPath("images/" + "key_green.png"), cached=False)))
		alist.append((_("Toggle repeat"), LoadPixmap(getSkinPath("images/" + "key_yellow.png"), cached=False)))
		alist.append(("", LoadPixmap(getSkinPath("images/" + "key_blue.png"), cached=False)))
		alist.append((_("Play/Pause"), LoadPixmap(getSkinPath("images/" + "key_playpause.png"), cached=False)))
		alist.append((_("Stop playback"), LoadPixmap(getSkinPath("images/" + "key_stop.png"), cached=False)))
		alist.append((_("Next song"), LoadPixmap(getSkinPath("images/" + "key_next.png"), cached=False)))
		alist.append((_("Previous song"), LoadPixmap(getSkinPath("images/" + "key_previous.png"), cached=False)))

		self["helplist"].setList(alist)
		self["helplist"].master.downstream_elements.setSelectionEnabled(0)


class MDCMusicPlayer(Screen, InfoBarBase, InfoBarSeek, InfoBarNotifications):

	IS_DIALOG = True

	def __init__(self, session, song_list, song_index):
		print("MDC: MusicPlayer: MDCMusicPlayer: __init__: song_index: %s, song_list: %s" % (song_index, str(song_list)))
		self.session = session
		self.song_list = song_list
		self.song_index = song_index
		self.song_index_list = range(len(song_list))

		Screen.__init__(self, session)
		InfoBarNotifications.__init__(self)
		InfoBarBase.__init__(self)
		self.skinName = self.__class__.__name__

		self["actions"] = ActionMap(
			["MDCActions"],
			{
				"exit":	self.exit,
				"back":	self.exit,
				"playpause": self.pause,
				"stop": self.stop,
				"right": self.playNext,
				"red": self.exit,
				"left": self.playPrevious,
				"green": self.shuffleList,
				"yellow": self.repeatSong,
				"help": self.help,
			},
			-1
		)

		self["Service"] = MDCCurrentService(session.nav, self)
		self["repeat"] = Pixmap()
		self["repeat"].hide()
		self["shuffle"] = Pixmap()
		self["shuffle"].hide()
		self["play"] = Pixmap()
		self["pause"] = Pixmap()
		self["pause"].hide()
		self["title"] = Label()
		self["album"] = Label()
		self["artist"] = Label()
		self["genre"] = Label()
		self["track"] = Label()
		self["next_title"] = Label()
		self["gapless"] = Pixmap()

		self.__event_tracker = ServiceEventTracker(
			screen=self,
			eventmap={
				iPlayableService.evUpdatedInfo: self.__evUpdatedInfo,
				iPlayableService.evUser + 10: self.__evAudioDecodeError,
				iPlayableService.evUser + 12: self.__evPluginError,
				iPlayableService.evUser + 13: self.embeddedCoverArt,
				iPlayableService.evStart: self.__serviceStarted,
				iPlayableService.evStopped: self.__serviceStopped,
			}
		)

		InfoBarSeek.__init__(self, actionmap="MediaPlayerSeekActions")
		self.service_started = False
		self.shuffle = False
		self.repeat = False
		self.current_filename = ""
		self.current_google_cover_file = ""
		self.current_title = None
		self.got_embedded_cover_art = False
		self.first_start = True
		self.onLayoutFinish.append(self.__layoutFinished)
		self.onShown.append(self.__onShown)
		self.sTitle = self.sAlbum = self.sArtist = self.sGenre = self.sYear = self.sTrackNumber = self.sTrackCount = ""

		eMerlinMusicPlayer.getInstance().setFunc(self.getNextFile)
		self["cover"] = MerlinMusicPlayerWidget()
		self["visual"] = MerlinMusicPlayerWidget()

	def __layoutFinished(self):
		#print("MDC: MusicPlayer: MDCMusicPlayer: startRun")
		self.GoogleCoverPathSetup()
		self.gaplessConfigSetup()
		self.alsasinkConfigSetup()

	def __onShown(self):
		if self.first_start:
			self.first_start = False
			self.setCover("")
			if self.song_list:
				self.playSong(self.song_list[self.song_index_list[self.song_index]][FILE_PATH])
		else:
			if self.current_title is not None:
				self.summaries.setText(self.current_title)

	def alsasinkConfigSetup(self):
		eMerlinMusicPlayer.getInstance().enableAlsa(config.plugins.mediacockpit.alsasink.value)

	def gaplessConfigSetup(self):
		eMerlinMusicPlayer.getInstance().enableGapless(config.plugins.mediacockpit.gapless.value)
		if config.plugins.mediacockpit.gapless.value:
			self["gapless"].show()
		else:
			self["gapless"].hide()

	def GoogleCoverPathSetup(self):
		self.googleDownloadDir = os.path.join(config.plugins.mediacockpit.googleimagepath.value, "")
		if not os.path.exists(self.googleDownloadDir):
			try:
				os.mkdir(self.googleDownloadDir)
			except Exception:
				self.googleDownloadDir = "/tmp/"

	def getNextFile(self, _arg):
		self.got_embedded_cover_art = False
		if not self.repeat:
			self.song_index = (self.song_index + 1) % len(self.song_list)
		filename = self.song_list[self.song_index_list[self.song_index]][FILE_PATH]
		self.current_filename = filename
		self["next_title"].setText(self.nextTitle())
		return filename

	def embeddedCoverArt(self):
		self.got_embedded_cover_art = True
		self.setCover("/tmp/.id3coverart")

	def setCover(self, filename):
		self["cover"].setCover(filename)

	def help(self):
		#print("MDC: MusicPlayer: help")
		self.session.open(MusicPlayerHelp)

	def exit(self):
		#print("MDC: MusicPlayer: song_index: %s" % self.song_index)
		eMerlinMusicPlayer.getInstance().setFunc(None)
		path = self.song_list[self.song_index_list[self.song_index]][FILE_PATH]
		self.close(path)

	def playSong(self, x):
		print("MDC-I: MusicPlayer: MDCMusicPlayer: playSong: x: %s" % str(x))
		self.service_started = False
		self.session.nav.stopService()
		self.sTitle = self.sAlbum = self.sArtist = self.sGenre = self.sYear = self.sTrackNumber = self.sTrackCount = ""
		self.seek = None
		self.current_filename = x[FILE_PATH]
		self.got_embedded_cover_art = False

		if config.plugins.mediacockpit.non_standard_decoder.value:
			sref = eServiceReference(ENIGMA_MERLINPLAYER_ID, 0, self.current_filename)
		else:
			sref = eServiceReference(sidDefault, 0, self.current_filename)

		self.session.nav.playService(sref)
		self["next_title"].setText(self.nextTitle())

	def __serviceStopped(self):
		#print("MDC: MusicPlayer: __serviceStopped: song_index: %s" % self.song_index)
		self.service_started = False

	def __serviceStarted(self):
		#print("MDC: MusicPlayer: __serviceStarted: song_index: %s" % self.song_index)
		self.service_started = True
		self["play"].show()
		self["pause"].hide()

	def __evUpdatedInfo(self):
		#print("MDC: MusicPlayer: __evUpdatedInfo: song_index: %s" % self.song_index)
		current_service = self.session.nav.getCurrentService()
		if current_service is not None:
			if not self.service_started:
				return
			if current_service.info().getInfoObject(iServiceInformation.sTagTrackGain) is None:
				return
			sTitle = current_service.info().getInfoString(iServiceInformation.sTagTitle)
			sAlbum = current_service.info().getInfoString(iServiceInformation.sTagAlbum)
			sArtist = current_service.info().getInfoString(iServiceInformation.sTagArtist)
			sGenre = current_service.info().getInfoString(iServiceInformation.sTagGenre)
			sYear = current_service.info().getInfoString(iServiceInformation.sTagDate)
			sTrackNumber = current_service.info().getInfo(iServiceInformation.sTagTrackNumber)
			sTrackCount = current_service.info().getInfo(iServiceInformation.sTagTrackCount)

			if sTitle == self.sTitle and sAlbum == self.sAlbum and sArtist == self.sArtist and sGenre == self.sGenre and sYear == self.sYear and sTrackNumber == self.sTrackNumber and sTrackCount == self.sTrackCount:
				return

			self.sTitle = sTitle
			self.sAlbum = sAlbum
			self.sArtist = sArtist
			self.sGenre = sGenre
			self.sYear = sYear
			self.sTrackNumber = sTrackNumber
			self.sTrackCount = sTrackCount

			track = ""
			if sTrackNumber and sTrackCount:
				track = "%s/%s" % (sTrackNumber, sTrackCount)
			elif sTrackNumber:
				track = str(sTrackNumber)
			if sYear:
				sYear = "(%s)" % sYear

			self.updateMusicInformation(sArtist, sTitle, sAlbum, sGenre, sYear, track, clear=True)
		else:
			self.setCover("")
			self.updateMusicInformation(clear=True)

	def updateMusicInformation(self, artist="", title="", album="", genre="", year="", track="", clear=False):
		if year and album:
			album_year = "%s %s" % (album, year)
		else:
			album_year = album

		self.updateSingleMusicInformation("artist", artist, clear)
		self.updateSingleMusicInformation("title", title, clear)
		self.updateSingleMusicInformation("album", album_year, clear)
		self.updateSingleMusicInformation("genre", genre, clear)
		self.updateSingleMusicInformation("track", track, clear)

		self.current_title = title
		self.summaries.setText(title)

		if not self.got_embedded_cover_art and not self.setFolderCover():
			self.updateCover(artist, album)

	def setFolderCover(self):
		adir = os.path.dirname(os.path.abspath(self.current_filename))
		cover_filenames = ["folder.png", "folder.jpg", "cover.jpg", "cover.png", "coverArt.jpg"]
		cover_art_filename = None
		for cover_filename in cover_filenames:
			path = os.path.join(adir, cover_filename)
			if fileExists(path):
				cover_art_filename = path
				self.got_embedded_cover_art = True
				#print("MDC: MusicPlayer: MDCMusicPlayer: setFolderCover: using cover from directory")
				self.setCover(cover_art_filename)
		return cover_art_filename is not None

	def updateCover(self, artist, album):
		if self.got_embedded_cover_art is False:
			if config.plugins.mediacockpit.usegoogleimage.value:
				self.getGoogleCover(artist, album)
			else:
				self.got_embedded_cover_art = True
				self.setCover("")
				self.current_google_cover_file = ""

	def updateSingleMusicInformation(self, name, info, clear):
		if info or clear:
			if self[name].getText() != info:
				self[name].setText(info)

	def getGoogleCover(self, artist, album):
		#print("MDC: MusicPlayer: MDCMusicPlayer: getGoogleCover: artist: %s, album: %s" % (artist, album))
		if artist and album:
			if artist and album:
				file_name_string = self.googleDownloadDir + "%s_%s" % (self.format_filename(artist), self.format_filename(album))
			else:
				file_name_string = self.googleDownloadDir + self.format_filename(self.sTitle)
			if os.path.exists(file_name_string):
				#print("MDC: MusicPlayer: MDCMusicPlayer: getGoogleCover: using cover from %s " % file_name_string)
				self.setCover(file_name_string)
			else:
				#print("MDC: MusicPlayer: MDCMusicPlayer: getGoogleCover: searching for cover at google")
				if artist and album:
					searchstr = quote("%s+%s" % (album, artist))
				else:
					searchstr = quote(self.sTitle)
				url = 'https://www.google.de/search?q=%s+-youtube&tbm=isch&source=lnt&tbs=isz:ex,iszw:500,iszh:500' % searchstr
				#print("MDC: MusicPlayer: MDCMusicPlayer: getGoogleCover: url: %s" % url)
				if self.current_google_cover_file != url:
					self.setCover("")
					self.current_google_cover_file = url
					getPage(url, timeout=4, agent='Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.56 Safari/537.17').addCallback(boundFunction(self.googleImageCallback, file_name_string)).addErrback(self.coverDownloadFailed)
		else:
			self.setCover("")

	def googleImageCallback(self, filename, result):
		#print("MDC: MusicPlayer: MDCMusicPlayer googleImageCallback: filename: %s, result: %s" % (filename, result))
		urlsraw = re.findall(',"ou":".+?","ow"', result)
		#print("MDC: MusicPlayer: MDCMusicPlayer: googleImageCallback: urlsraw: %s" % urlsraw)
		imageurls = [urlraw[7:-6].encode() for urlraw in urlsraw] # new on 08.02.2017 imageurls=[urlraw[14:-14].encode() for urlraw in urlsraw]
		#print("MDC: MusicPlayer: MDCMusicPlayer: googleImageCallback: imageurls: %s" % imageurls)
		if imageurls:
			#print("MDC: MusicPlayer: MDCMusicPlayer: googleImageCallback: downloading cover from %s " % imageurls[0])
			downloadPage(imageurls[0], filename).addCallback(boundFunction(self.coverDownloadFinished, filename)).addErrback(self.coverDownloadFailed)
		else:
			#print("MDC: MusicPlayer: MDCMusicPlayer: googleImageCallback: no image found")
			self.setCover("")

	def format_filename(self, filename):
		f = "".join([c for c in filename if c.isalpha() or c.isdigit() or c == ' '])
		return f.replace(" ", "_")

	def coverDownloadFailed(self, result):
		print("MDC-E: Music MDCMusicPlayer: coverDownloadFailed: %s " % result)
		self.setCover("")

	def coverDownloadFinished(self, filename, _result):
		#print("MDC: MusicPlayer: MDCMusicPlayer: coverDownloadFinished")
		self.setCover(filename)

	def __resetSingleMusicInformation(self):
		self.updateSingleMusicInformation("artist", "", True)
		self.updateSingleMusicInformation("album", "", True)
		self.updateSingleMusicInformation("genre", "", True)
		self.updateSingleMusicInformation("track", "", True)
		self.updateSingleMusicInformation("title", self.current_filename, True)

	def __evAudioDecodeError(self):
		self.__resetSingleMusicInformation()
		current_service = self.session.nav.getCurrentService()
		sAudioType = current_service.info().getInfoString(iServiceInformation.sUser + 10)
		message = _("This Dreambox can't decode %s streams!") % sAudioType
		#print("MDC: MusicPlayer: MDCMusicPlayer: __evAudioDecodeError: %s" % message)
		self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=20)

	def __evPluginError(self):
		self.__resetSingleMusicInformation()
		current_service = self.session.nav.getCurrentService()
		message = current_service.info().getInfoString(iServiceInformation.sUser + 12)
		#print("MDC: MusicPlayer: MDCMusicPlayer: __evPluginError: %s" % message)
		self.session.open(MessageBox, message, type=MessageBox.TYPE_INFO, timeout=20)

	def doEofInternal(self, playing):
		print("MDC: MusicPlayer: doEofInternal: playing: %s" % playing)
		if playing:
			self.playNext()

	def checkSkipShowHideLock(self):
		self.updatedSeekState()

	def updatedSeekState(self):
		if self.seekstate == self.SEEK_STATE_PAUSE:
			self["pause"].show()
			self["play"].hide()
		elif self.seekstate == self.SEEK_STATE_PLAY:
			self["play"].show()
			self["pause"].hide()

	def pause(self):
		self.pauseService()

	def play(self):
		self.playSong(self.song_list[self.song_index_list[self.song_index]][FILE_PATH])

	def stop(self):
		self.seek = None
		self.session.nav.stopService()
		self.exit()

	def playNext(self):
		if not self.repeat:
			self.song_index = nextIndex(self.song_index, len(self.song_list))
		self.playSong(self.song_list[self.song_index_list[self.song_index]])

	def playPrevious(self):
		if not self.repeat:
			self.song_index = previousIndex(self.song_index, len(self.song_list))
		self.playSong(self.song_list[self.song_index_list[self.song_index]])

	def nextTitle(self):
		next_index = self.song_index
		if not self.repeat:
			next_index = nextIndex(self.song_index, len(self.song_list))
		audio, _is_audio, title, _genre, artist, _album, _tracknr, _track, _date, _length, _bitrate = getID3Tags(self.song_list[self.song_index_list[next_index]][FILE_PATH])
		text = title
		if audio and artist:
			text = "%s - %s" % (title, artist)
		return str(text)

	def shuffleList(self):
		self.shuffle = not self.shuffle
		if self.shuffle:
			self["shuffle"].show()
			shuffle(self.song_index_list)
			self.song_index = len(self.song_list) - 1
		else:
			self["shuffle"].hide()
			self.song_index_list = range(len(self.song_list))
			for i, index in enumerate(self.song_index_list):
				if index == self.song_index:
					self.song_index = i
					break
		self["next_title"].setText(self.nextTitle())

	def repeatSong(self):
		self.repeat = not self.repeat
		if self.repeat:
			self["repeat"].show()
			self["next_title"].setText(self["title"].getText())
		else:
			self["repeat"].hide()
			self["next_title"].setText(self.nextTitle())

	def createSummary(self):
		return MDCMusicPlayerSummary
