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


from Components.ActionMap import HelpableActionMap
from Screens.InfoBarGenerics import InfoBarSeek
from enigma import eTimer
from .__init__ import _
from .Debug import logger
from .CutListUtils import secondsToPts, ptsToSeconds
from .BoxUtils import getBoxType


SKIP_TIMEOUT = 5000  # milliseconds
STOP_BEFORE_EOF = 5  # seconds


class CockpitSmartSeek(InfoBarSeek):

    def __init__(self, event_start, config_skip_first_long):
        logger.info("...")
        InfoBarSeek.__init__(self)

        self["InfoBarSmartSeek"] = HelpableActionMap(
            self,
            "InfoBarSmartSeekActions",
            {
                "CHANNELUP":	(self.skipForward,	_("Skip forward")),
                "CHANNELDOWN":	(self.skipBackward,	_("Skip backward")),
            },
            prio=-1
        )

        self.event_start = event_start
        self.skip_first = True
        self.config_skip_first_long = config_skip_first_long
        self.skip_forward = True
        self.skip_index = 0
        self.skip_distance_long = [300, 60, 30, 15]
        self.skip_distance_short = [60, 30, 15]
        self.skip_distance = self.skip_distance_long
        self.reset_skip_timer = eTimer()
        self.reset_skip_timer_conn = self.reset_skip_timer.timeout.connect(self.resetSkipTimer)

    def skipToEventStart(self):
        logger.info("...")
        _, _, _, event_start_time, recording_start_time = self.getEventInfo()
        self.doSkip(event_start_time - recording_start_time)

    def resetSkipTimer(self):
        logger.info("...")
        self.skip_first = True
        self.skip_distance = self.skip_distance_long
        self.skip_index = 0
        self.skip_forward = True
        self.showPVRStatePic(True)

    def setSkipDistance(self):
        if self.skip_first and self.event_start:
            _, _, _, event_start_time, recording_start_time = self.getEventInfo()
            logger.debug("position: %s, event_start_time: %s", ptsToSeconds(self.getPosition()), event_start_time)
            if abs(event_start_time - recording_start_time - ptsToSeconds(self.getSeekPosition())) <= 60:
                self.skip_distance = self.skip_distance_short
            else:
                self.skip_distance = self.skip_distance_long
            logger.debug("skip_distance: %s", self.skip_distance)

    def skipForward(self):
        logger.info("...")
        self.reset_skip_timer.start(SKIP_TIMEOUT, True)
        self.setSkipDistance()
        if not self.skip_first and (not self.skip_forward or (self.config_skip_first_long and self.skip_distance == self.skip_distance_long and self.skip_index == 0)):
            self.skip_index = len(self.skip_distance) - 1 if self.skip_index >= len(self.skip_distance) - 1 else self.skip_index + 1
        self.skip_forward = True
        self.skip_first = False
        distance = self.skip_distance[self.skip_index]
        position = ptsToSeconds(self.getSeekPosition())
        self.showPVRStatePic(False)
        self.doSkip(position + distance)

    def skipBackward(self):
        logger.info("...")
        self.reset_skip_timer.start(SKIP_TIMEOUT, True)
        self.setSkipDistance()
        if not self.skip_first and self.skip_forward:
            self.skip_index = len(self.skip_distance) - 1 if self.skip_index >= len(self.skip_distance) - 1 else self.skip_index + 1
        self.skip_forward = False
        self.skip_first = False
        distance = self.skip_distance[self.skip_index]
        position = ptsToSeconds(self.getSeekPosition())
        distance = min(distance, position)
        self.doSkip(position - distance)

    def doSkip(self, target):
        length = ptsToSeconds(self.getSeekLength())
        if target > length - STOP_BEFORE_EOF:
            target = length - STOP_BEFORE_EOF
        target = max(0, target)
        logger.info("target: %s, length: %s", target, length)
        if length:
            self.doSeek(secondsToPts(target))
        self.showAfterSeek()

    def recoverEoFFailure(self):
        logger.info("skip_forward: %s, skip_index: %s", self.skip_forward, self.skip_index)
        length = ptsToSeconds(self.getSeekLength())
        target = max(0, length - STOP_BEFORE_EOF)
        logger.debug("length: %s, target: %s", length, target)
        if not getBoxType().startswith("dream"):
            self.doSeek(secondsToPts(target))
        else:
            self.doSeekRelative(-secondsToPts(STOP_BEFORE_EOF))
