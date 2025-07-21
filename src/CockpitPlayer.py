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


from enigma import iPlayableService
from Components.ActionMap import HelpableActionMap
from Components.config import config
from Components.ServiceEventTracker import InfoBarBase, ServiceEventTracker
from Components.Sources.COCCurrentService import COCCurrentService
from Screens.Screen import Screen
from Screens.HelpMenu import HelpableScreen
from Screens.MessageBox import MessageBox
from Screens.InfoBarGenerics import InfoBarAudioSelection, InfoBarShowHide, InfoBarNotifications, Notifications, InfoBarSubtitleSupport
from ServiceReference import ServiceReference
from .Debug import logger
from .__init__ import _
from .CutList import CutList
from .CutListUtils import ptsToSeconds, getCutListLast, getCutListFirst
from .RecordingUtils import isRecording
from .SkinUtils import getSkinName
from .CockpitCueSheet import CockpitCueSheet
from .CockpitPVRState import CockpitPVRState
from .CockpitSeek import CockpitSeek
from .MovieInfoEPG import MovieInfoEPG
from .BoxUtils import getBoxType


class CockpitPlayerSummary(Screen):

    def __init__(self, session, parent):
        Screen.__init__(self, session, parent)
        self.skinName = getSkinName("CockpitPlayerSummary")


class CockpitPlayer(
        Screen, HelpableScreen, InfoBarBase, InfoBarNotifications, InfoBarShowHide, InfoBarAudioSelection, InfoBarSubtitleSupport,
        CockpitCueSheet, CockpitSeek, CockpitPVRState, CutList):

    ENABLE_RESUME_SUPPORT = False
    ALLOW_SUSPEND = True

    def __init__(self, session, service, config_plugins_plugin, leave_on_eof=False, recording_start_time=0, timeshift=None, service_center=None):
        self.service = service
        self.config_plugins_plugin = config_plugins_plugin
        self.leave_on_eof = leave_on_eof

        self.allowPiP = False
        self.allowPiPSwap = False

        Screen.__init__(self, session)
        HelpableScreen.__init__(self)
        self.skinName = getSkinName("CockpitPlayer")
        self["Service"] = COCCurrentService(session.nav, self)

        InfoBarShowHide.__init__(self)
        InfoBarBase.__init__(self)
        InfoBarAudioSelection.__init__(self)
        InfoBarNotifications.__init__(self)
        InfoBarSubtitleSupport.__init__(self)
        CockpitCueSheet.__init__(self, service)
        CutList.__init__(self)

        self["actions"] = HelpableActionMap(
            self,
            "CockpitActions",
            {
                "STOP":	(self.leavePlayer, _("Stop playback")),
                "EXIT":	(self.leavePlayer, _("Stop playback")),
                "POWER": (self.leavePlayer, _("Stop playback")),
                "CHANNELUP": (self.skipForward,	_("Skip forward")),
                "CHANNELDOWN": (self.skipBackward, _("Skip backward")),
                "INFOS": (self.infoMovie, _("EPG Info")),
            },
            -2
        )

        self._event_tracker = ServiceEventTracker(
            screen=self,
            eventmap={
                iPlayableService.evStart: self.__serviceStarted,
            }
        )

        event_start = config_plugins_plugin.movie_start_position.value == "event_start"
        CockpitSeek.__init__(self, session, service, event_start,
                             recording_start_time, timeshift, service_center)
        CockpitPVRState.__init__(self)

        self.service_started = False
        self.cut_list = []
        self.resume_point = 0

        self.onShown.append(self.__onShown)

    def createSummary(self):
        return CockpitPlayerSummary

    def __onShown(self):
        logger.info("...")
        if not self.service_started:
            self.session.nav.playService(self.service)

    def __serviceStarted(self):
        logger.info("self.is_closing: %s", self.is_closing)
        if not self.service_started and not self.is_closing:
            self.service_started = True
            self.downloadCuesheet()
            if self.config_plugins_plugin.movie_resume_at_last_pos.value:
                self.resume_point = getCutListLast(self.cut_list)
                if self.resume_point > 0:
                    seconds = ptsToSeconds(self.resume_point)
                    logger.debug("resume_point: %s", seconds)
                    Notifications.AddNotificationWithCallback(
                        self.__serviceStartedCallback,
                        MessageBox,
                        _("Do you want to resume playback at position: %d:%02d:%02d?")
                        % (seconds / 3600, seconds % 3600 / 60, seconds % 60),
                        timeout=10,
                        type=MessageBox.TYPE_YESNO,
                        default=False,
                    )
                else:
                    self.__serviceStartedCallback(False)
            else:
                self.__serviceStartedCallback(False)

    def __serviceStartedCallback(self, answer):
        logger.info("answer: %s", answer)
        if answer:
            self.doSeek(self.resume_point)
        else:
            if self.config_plugins_plugin.movie_start_position.value == "first_mark":
                self.doSeek(getCutListFirst(self.cut_list, config.recording.margin_before.value * 60))
            if self.config_plugins_plugin.movie_start_position.value == "event_start":
                self.skipToEventStart()
            if self.config_plugins_plugin.movie_start_position.value == "beginning":
                self.doSeek(0)

    def showPVRStatePic(self, show):
        self.show_state_pic = show

    def leavePlayer(self):
        logger.info("...")
        self.updateCutList(self.service.getPath(), last=self.getPosition())
        self.session.nav.stopService()
        self.close()

    def doEofInternal(self, playing):
        logger.info("playing: %s, self.execing: %s", playing, self.execing)
        if self.execing:
            if isRecording(self.service.getPath()) or self.timeshift:
                if not getBoxType().startswith("dream"):
                    self.session.nav.stopService()
                self.session.nav.playService(self.service)
                self.recoverEoFFailure()
            else:
                self.is_closing = True
            if self.leave_on_eof:
                self.leavePlayer()

    def infoMovie(self):
        event = self.getEvent()
        if event:
            self.session.open(MovieInfoEPG, event,
                              ServiceReference(self.service))

    def showMovies(self):
        logger.info("...")
