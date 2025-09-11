#!/usr/bin/python
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
from random import shuffle
from enigma import eServiceReference, iPlayableService, iServiceInformation
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Components.ActionMap import HelpableActionMap
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.Sources.COCCurrentService import COCCurrentService
from Components.ServiceEventTracker import ServiceEventTracker
from Components.config import config
try:
    from Components.MerlinMusicPlayerWidget import MerlinMusicPlayerWidget
    from merlin_musicplayer.emerlinmusicplayer import eMerlinMusicPlayer
    import merlin_musicplayer._emerlinmusicplayer  # noqa: F401, pylint: disable=W0611
except ImportError:
    from .MerlinMusicPlayer import MerlinMusicPlayerWidget
    from .MerlinMusicPlayer import eMerlinMusicPlayer
from .__init__ import _
from .Debug import logger
from .FileManagerUtils import MDC_IDX_PATH
from .ID3Tags import getID3Tags
from .ServiceUtils import SID_GST, getService
from .FileListUtils import previousIndex, nextIndex
from .CoverLastFM import CoverLastFM
from .FileUtils import deleteFile
from .SkinUtils import getSkinName
from .CockpitSeek import CockpitSeek
from .CockpitCueSheet import CockpitCueSheet


ENIGMA_MERLINPLAYER_ID = 0x1019


class CockpitMusicPlayerSummary(Screen):

    def __init__(self, session, parent):
        Screen.__init__(self, session)
        self.skinName = getSkinName(self.__class__.__name__)
        self["title"] = Label()
        self["Service"] = COCCurrentService(session.nav, parent)

    def setText(self, text):
        self["title"].setText(text)


class CockpitMusicPlayer(Screen, HelpableScreen, CockpitSeek, CockpitCueSheet):

    def __init__(self, session, song_list, song_index, service_center):
        logger.debug("song_index: %s, song_list: %s",
                     song_index, str(song_list))
        self.song_list = song_list
        self.song_index = song_index
        self.song_index_list = list(range(len(song_list)))

        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.skinName = getSkinName(self.__class__.__name__)
        service = getService(song_list[song_index][MDC_IDX_PATH])
        CockpitSeek.__init__(self, session, service,
                             False, 0, None, service_center)
        CockpitCueSheet.__init__(self, service)

        self.cover_downloader = None
        if config.plugins.mediacockpit.cover_downloader.value == "lastfm":
            self.cover_downloader = CoverLastFM(
                config.plugins.mediacockpit.cover_download_path.value,
                self.coverDownloadFinished, self.coverDownloadFailed
            )

        self["actions"] = HelpableActionMap(
            self,
            "CockpitActions",
            {
                "EXIT":	(self.exit, _("Exit")),
                "PLAY":	(self.playpause, _("Play/Pause") + " " + _("Song")),
                "STOP":	(self.stop, _("Stop playback")),
                "RIGHTR": (self.playNext, _("Next song")),
                "RED": (self.exit, _("Exit")),
                "LEFTR": (self.playPrevious, _("Previous song")),
                "GREEN": (self.toggleShuffle, _("Toggle shuffle")),
                "YELLOW": (self.toggleRepeat, _("Toggle repeat")),
            },
            -1
        )

        self["Service"] = COCCurrentService(session.nav, self)
        self["play"] = Pixmap()
        self["pause"] = Pixmap()
        self["pause"].hide()
        self["title"] = Label()
        self["album"] = Label()
        self["artist"] = Label()
        self["genre"] = Label()
        self["track"] = Label()
        self["next_title"] = Label()
        self["shuffle"] = Pixmap()
        self["shuffle"].hide()
        self["shuffle_off"] = Pixmap()
        self["repeat"] = Pixmap()
        self["repeat"].hide()
        self["repeat_off"] = Pixmap()
        self["gapless"] = Pixmap()
        self["gapless"].hide()
        self["gapless_off"] = Pixmap()

        self._event_tracker = ServiceEventTracker(
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

        self.service_started = False
        self.shuffle = False
        self.repeat = False
        self.current_filename = ""
        self.current_title = None
        self.got_embedded_cover_art = False
        self.first_start = True
        self.onLayoutFinish.append(self.LayoutFinish)
        self.sTitle = self.sAlbum = self.sArtist = self.sGenre = self.sYear = self.sTrackNumber = self.sTrackCount = ""
        eMerlinMusicPlayer.getInstance().setFunc(self.getNextFile)
        self["cover"] = MerlinMusicPlayerWidget()
        self["visual"] = MerlinMusicPlayerWidget()

    def LayoutFinish(self):
        logger.debug("...")
        self.gaplessConfigSetup()
        self.alsasinkConfigSetup()

        if self.first_start:
            self.first_start = False
            self["cover"].setCover("")

            if self.song_list:
                self.playSong(
                    self.song_list[self.song_index_list[self.song_index]])
        else:
            if self.current_title is not None:
                self.summaries.setText(self.current_title)

    def showPVRStatePic(self, show):
        self.show_state_pic = show

    def alsasinkConfigSetup(self):
        eMerlinMusicPlayer.getInstance().enableAlsa(
            config.plugins.mediacockpit.alsasink.value)

    def gaplessConfigSetup(self):
        eMerlinMusicPlayer.getInstance().enableGapless(
            config.plugins.mediacockpit.gapless.value)
        if config.plugins.mediacockpit.gapless.value:
            self["gapless"].show()
            self["gapless_off"].hide()
        else:
            self["gapless"].hide()
            self["gapless_off"].show()

    def getNextFile(self, _arg):
        self.got_embedded_cover_art = False
        if not self.repeat:
            self.song_index = nextIndex(self.song_index, len(self.song_list))
        filename = self.song_list[self.song_index_list[self.song_index]][MDC_IDX_PATH]
        self.current_filename = filename
        self["next_title"].setText(self.nextTitle())
        return filename

    def embeddedCoverArt(self):
        self.got_embedded_cover_art = True
        self["cover"].setCover("/tmp/.id3coverart")

    def exit(self):
        logger.debug("song_index: %s", self.song_index)
        eMerlinMusicPlayer.getInstance().setFunc(None)
        path = self.song_list[self.song_index_list[self.song_index]][MDC_IDX_PATH]
        self.close(path)

    def playSong(self, afile):
        logger.info("afile: %s", str(afile))
        self.service_started = False
        self.session.nav.stopService()
        self.sTitle = self.sAlbum = self.sArtist = self.sGenre = self.sYear = self.sTrackNumber = self.sTrackCount = ""
        self.current_filename = afile[MDC_IDX_PATH]
        self.got_embedded_cover_art = False

        if config.plugins.mediacockpit.non_standard_decoder.value:
            sref = eServiceReference(
                ENIGMA_MERLINPLAYER_ID, 0, self.current_filename)
        else:
            sref = eServiceReference(SID_GST, 0, self.current_filename)

        self.session.nav.playService(sref)
        self["next_title"].setText(self.nextTitle())

    def __serviceStopped(self):
        logger.debug("song_index: %s", self.song_index)
        self.service_started = False

    def __serviceStarted(self):
        logger.debug("song_index: %s", self.song_index)
        self.service_started = True
        self["play"].show()
        self["pause"].hide()

    def __evUpdatedInfo(self):
        logger.debug("song_index: %s", self.song_index)
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
            sTrackNumber = current_service.info().getInfo(
                iServiceInformation.sTagTrackNumber)
            sTrackCount = current_service.info().getInfo(iServiceInformation.sTagTrackCount)

            if sTitle == self.sTitle and sAlbum == self.sAlbum and sArtist == self.sArtist \
                    and sGenre == self.sGenre and sYear == self.sYear and sTrackNumber == self.sTrackNumber \
                    and sTrackCount == self.sTrackCount:
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
                track = "%s" % sTrackNumber
            if sYear:
                sYear = "(%s)" % sYear

            self.updateMusicInformation(
                sArtist, sTitle, sAlbum, sGenre, sYear, track)
        else:
            self["cover"].setCover("")
            self.updateMusicInformation("", "", "", "", "", "")

    def updateMusicInformation(self, artist, title, album, genre, year, track):
        if album and year:
            album = "%s %s" % (album, year)

        self["artist"].setText(artist)
        self["title"].setText(title)
        self["album"].setText(album)
        self["genre"].setText(genre)
        self["track"].setText(track)

        self.current_title = title
        self.summaries.setText(title)

        if not self.got_embedded_cover_art and not self.setFolderCover():
            self.updateCover(artist, album, title)

    def setFolderCover(self):
        adir = os.path.dirname(os.path.abspath(self.current_filename))
        cover_filenames = ["folder.png", "Folder.png", "folder.jpg", "Folder.jpg",
                           "cover.jpg", "Cover.jpg", "cover.png", "Cover.png", "coverArt.jpg"]
        cover_art_filename = None
        for cover_filename in cover_filenames:
            path = os.path.join(adir, cover_filename)
            if os.path.exists(path):
                cover_art_filename = path
                self.got_embedded_cover_art = True
                logger.debug("using cover from directory")
                self["cover"].setCover(cover_art_filename)
        return cover_art_filename is not None

    def updateCover(self, artist, album, title):
        if self.cover_downloader and self.got_embedded_cover_art is False:
            self.cover_downloader.getCover(artist, album, title)
        else:
            self.got_embedded_cover_art = True
            self["cover"].setCover("")

    def coverDownloadFailed(self, result):
        logger.error("result: %s ", result)
        self["cover"].setCover("")

    def coverDownloadFinished(self, path, _result):
        logger.debug("path: %s", path)
        if os.path.getsize(path):
            self["cover"].setCover(path)
        else:
            deleteFile(path)

    def __resetMusicInformation(self):
        self["artist"].setText("")
        self["album"].setText("")
        self["genre"].setText("")
        self["track"].setText("")
        self["title"].setText(self.current_filename)

    def __evAudioDecodeError(self):
        self.__resetMusicInformation()
        current_service = self.session.nav.getCurrentService()
        sAudioType = current_service.info().getInfoString(iServiceInformation.sUser + 10)
        message = _("This Dreambox can't decode %s streams!") % sAudioType
        logger.debug("message: %s", message)
        self.session.open(MessageBox, message,
                          type=MessageBox.TYPE_INFO, timeout=20)

    def __evPluginError(self):
        self.__resetMusicInformation()
        current_service = self.session.nav.getCurrentService()
        message = current_service.info().getInfoString(iServiceInformation.sUser + 12)
        logger.debug("message: %s", message)
        self.session.open(MessageBox, message,
                          type=MessageBox.TYPE_INFO, timeout=20)

    def doEofInternal(self, playing):
        logger.debug("playing: %s", playing)
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

    def playpause(self):
        self.playpauseService()

    def stop(self):
        self.session.nav.stopService()
        self.exit()

    def playNext(self):
        if not self.repeat:
            self.song_index = nextIndex(self.song_index, len(self.song_list))
        self.playSong(self.song_list[self.song_index_list[self.song_index]])

    def playPrevious(self):
        if not self.repeat:
            self.song_index = previousIndex(
                self.song_index, len(self.song_list))
        self.playSong(self.song_list[self.song_index_list[self.song_index]])

    def nextTitle(self):
        next_index = self.song_index
        if not self.repeat:
            next_index = nextIndex(self.song_index, len(self.song_list))
        audio, title, _genre, artist, _album, _tracknr, _track, _date, _length, _bitrate = getID3Tags(
            self.song_list[self.song_index_list[next_index]][MDC_IDX_PATH])
        if title is None:
            title = ""
        if audio and artist:
            title = "%s - %s" % (title, artist)
        return title

    def toggleShuffle(self):
        self.shuffle = not self.shuffle
        if self.shuffle:
            self["shuffle"].show()
            self["shuffle_off"].hide()
            shuffle(self.song_index_list)
        else:
            self["shuffle"].hide()
            self["shuffle_off"].show()
            self.song_index_list = list(range(len(self.song_list)))
        for i, index in enumerate(self.song_index_list):
            if index == self.song_index:
                self.song_index = i
                break
        self["next_title"].setText(self.nextTitle())

    def toggleRepeat(self):
        self.repeat = not self.repeat
        if self.repeat:
            self["repeat"].show()
            self["repeat_off"].hide()
        else:
            self["repeat"].hide()
            self["repeat_off"].show()
        self["next_title"].setText(self.nextTitle())

    def createSummary(self):
        return CockpitMusicPlayerSummary
