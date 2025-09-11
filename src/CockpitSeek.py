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


from time import time
from .Debug import logger
from .CutListUtils import secondsToPts, ptsToSeconds
from .ServiceUtils import SID_DVB
from .RecordingUtils import isRecording
from .CockpitSmartSeek import CockpitSmartSeek
from .CockpitEvent import CockpitEvent


class CockpitSeek(CockpitSmartSeek, CockpitEvent):

    def __init__(self, session, service, event_start, recording_start_time, timeshift, service_center):
        self.service = service
        self.timeshift = timeshift
        self.path = self.service.getPath()
        CockpitSmartSeek.__init__(self, event_start, True)
        CockpitEvent.__init__(self, session, service, recording_start_time, service_center)

    def isRecording(self):
        is_recording = isRecording(self.path) or self.timeshift
        return is_recording

    def getLength(self):
        length = 0
        if self.service_started:
            if self.service.type == SID_DVB:
                _, _, length, _, _ = self.getEventInfo()
                length = secondsToPts(length)
            if not length:
                length = self.getSeekLength()
        logger.info("length: %ss (%s)", ptsToSeconds(length), length)
        return length

    def getSeekLength(self):
        length = 0
        seek = self.getSeek()
        if seek and self.service_started:
            seek_len = seek.getLength()
            if not seek_len[0]:
                length = seek_len[1]
        logger.info("length: %ss (%s)", ptsToSeconds(length), length)
        return length

    def getPosition(self):
        position = 0
        if self.service_started:
            before, offset, _, _, _ = self.getEventInfo()
            position = self.getSeekPosition() - secondsToPts(offset) + secondsToPts(before)
        logger.debug("position: %ss (%s)", ptsToSeconds(position), position)
        return position

    def getRecordingLength(self):
        _, _, _, _, recording_start_time = self.getEventInfo()
        length = secondsToPts(int(time()) - recording_start_time)
        logger.debug("recording_length: %ss (%s)", ptsToSeconds(length), length)
        return length

    def getRecordingPosition(self):
        position = 0
        if self.service_started:
            if self.isRecording():
                before, offset, _, _, recording_start_time = self.getEventInfo()
                position = secondsToPts(int(time()) - recording_start_time - offset + before)
        logger.debug("recording_position: %ss (%s)", ptsToSeconds(position), position)
        return position

    def getSeekPosition(self):
        position = 0
        seek = self.getSeek()
        if seek and self.service_started:
            pos = seek.getPlayPosition()
            if not pos[0] and pos[1] > 0:
                position = pos[1]
        logger.info("position: %ss (%s)", ptsToSeconds(position), position)
        return position

    def getBeforePosition(self):
        position = 0
        if self.service_started:
            before, _, _, _, _ = self.getEventInfo()
            position = secondsToPts(before)
        logger.debug("before_position: %ss (%s)", ptsToSeconds(position), position)
        return position
