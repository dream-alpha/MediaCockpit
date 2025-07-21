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


from datetime import datetime
from .Debug import logger


class CockpitEvent():

    def __init__(self, _session, service, _recording_start_time, service_center):
        self.service = service
        self.service_center = service_center

    def getEvent(self):
        return self.service_center.info(self.service).getEvent()

    def getInfo(self):
        return self.service_center.info(self.service)

    def getEventInfo(self):
        logger.info("...")
        event_start_time = self.service_center.info(self.service).info.getEventStartTime()
        recording_start_time = self.service_center.info(self.service).info.getRecordingStartTime()
        event_length = self.service_center.info(self.service).info.getLength()
        if recording_start_time and event_start_time > recording_start_time:
            event_length += event_start_time - recording_start_time
        before = 0
        if event_start_time < recording_start_time:
            before = recording_start_time - event_start_time
        offset = 0
        logger.debug("before: %s, event_start_time: %s, recording_start_time: %s, length: %s", before, datetime.fromtimestamp(event_start_time), datetime.fromtimestamp(recording_start_time), event_length)
        return before, offset, event_length, event_start_time, recording_start_time
