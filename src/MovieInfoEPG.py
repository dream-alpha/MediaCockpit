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


from Screens.EventView import EventViewSimple
from .__init__ import _


class MovieInfoEPG(EventViewSimple):

    def __init__(self, session, event, service_reference):
        EventViewSimple.__init__(self, session, event, service_reference)
        self.skinName = ["EventViewSimple", "EventView"]

    def setService(self, service):
        EventViewSimple.setService(self, service)
        if self.isRecording:
            self["channel"].setText("")

    def setEvent(self, event):
        EventViewSimple.setEvent(self, event)
        if self.isRecording and event.getDuration() == 0:
            self["duration"].setText("")
        else:
            self["duration"].setText(
                ("%d" % (event.getDuration() / 60)) + " " + _("min"))
            self["datetime"].setText(event.getBeginTimeString())
