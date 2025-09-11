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
from datetime import datetime
from enigma import eServiceCenter, iServiceInformation
from Components.config import config
from .Debug import logger


instance = None


class ServiceCenter():

    def __init__(self):
        logger.debug("...")

    @staticmethod
    def getInstance():
        global instance
        if instance is None:
            instance = ServiceCenter()
        return instance

    def info(self, service):
        logger.debug("...")
        return ServiceInfo(service)


class ServiceInfo():

    def __init__(self, service):
        logger.debug("service.getPath(): %s", service.getPath())
        self.info = None
        if service:
            self.info = Info(service)

    def getLength(self, _service=None):
        logger.debug("..")
        return self.info and self.info.getLength()

    def getInfoString(self, _service=None, info_type=None):
        logger.debug("info_type: %s", info_type)
        if info_type == iServiceInformation.sServiceref:
            return self.info and self.info.getServiceReference()
        if info_type == iServiceInformation.sDescription:
            return self.info and self.info.getShortDescription()
        if info_type == iServiceInformation.sTags:
            return self.info and self.info.getTags()
        return "None"

    def getInfo(self, _service=None, info_type=None):
        logger.debug("info_type: %s", info_type)
        if info_type == iServiceInformation.sTimeCreate:
            return self.info and self.info.getEventStartTime()
        return None

    def getInfoObject(self, _service=None, info_type=None):
        logger.debug("info_type: %s", info_type)
        if info_type == iServiceInformation.sFileSize:
            return self.info and self.info.getSize()
        return None

    def getName(self, _service=None):
        logger.debug("...")
        return self.info and self.info.getName()

    def getEvent(self, _service=None):
        logger.debug("...")
        return self.info

    def getEventStartTime(self, _service=None):
        logger.debug("...")
        return self.info and self.info.getEventStartTime()

    def getRecordingStartTime(self, _service=None):
        logger.debug("...")
        return self.info and self.info.getRecordingStartTime()


class Info():

    def __init__(self, service):
        self.path = service.getPath()
        logger.debug("path: %s", self.path)
        self.file_type, self.name, self.short_description, self.extended_description, self.service_reference, self.cuts, self.tags = "", "", "", "", "", "", ""
        self.size = self.length = self.event_start_time = self.recording_start_time = 0
        if self.path:
            info = eServiceCenter.getInstance().info(service)
            self.length = info.getLength(service) if self.length < 86400 else 0
            if os.path.isfile(self.path):
                self.event_start_time = self.recording_start_time = int(
                    os.stat(self.path).st_ctime)
            else:
                self.event_start_time = self.recording_start_time = 0
            self.name = os.path.basename(self.path)

    def getName(self):
        # EventName NAME
        logger.debug("name: %s", self.name)
        return self.name

    def getServiceReference(self):
        logger.debug("...")
        return self.service_reference

    def getTags(self):
        logger.debug("...")
        return self.tags

    def getEventId(self):
        logger.debug("...")
        return 0

    def getEventName(self):
        logger.debug("...")
        return self.name

    def getShortDescription(self):
        logger.debug("...")
        # EventName SHORT_DESCRIPTION
        return self.short_description

    def getExtendedDescription(self):
        logger.debug("...")
        # EventName EXTENDED_DESCRIPTION
        return self.extended_description

    def getBeginTimeString(self):
        logger.debug("...")
        movie_date_format = config.plugins.mediacockpit.movie_date_format.value
        return datetime.fromtimestamp(self.event_start_time).strftime(movie_date_format)

    def getEventStartTime(self):
        logger.debug("...")
        return self.event_start_time

    def getRecordingStartTime(self):
        logger.debug("...")
        return self.recording_start_time

    def getDuration(self):
        logger.debug("...")
        return self.length

    def getLength(self):
        logger.debug("path: %s, length: %s", self.path, self.length)
        return self.length

    def getSize(self):
        logger.debug("...")
        return self.size
