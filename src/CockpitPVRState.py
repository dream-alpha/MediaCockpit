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

# pylint: disable=E1101


from enigma import eSize
from Screens.Screen import Screen
from Components.Label import Label
from Components.Pixmap import Pixmap
from Components.config import config
from Tools.LoadPixmap import LoadPixmap
from .__init__ import _
from .Debug import logger
from .SkinUtils import getSkinPath


class ScreenPVRState(Screen):

    def __init__(self, session):
        Screen.__init__(self, session)
        self["state"] = Label()
        self["state_pic"] = Pixmap()


class CockpitPVRState():

    def __init__(self):
        self.on_play_state_changed = self.onPlayStateChanged[:]
        self.onPlayStateChanged = [self.playStateChanged]
        self.pvr_state_dialog = self.session.instantiateDialog(ScreenPVRState)
        self.pvr_state_dialog.neverAnimate()
        self.show_state_pic = True

        self.onShow.append(self.mayShow)
        self.onHide.append(self.pvr_state_dialog.hide)
        self.onClose.append(self.delPvrState)

    def playStateChanged(self, state):
        logger.info("state: %s", state)
        play_state = state[3]
        logger.debug("play_state: %s", play_state)
        state_pic = "dvr_stop.svg"
        factor = ""
        if play_state == ">":
            state_pic = "dvr_play.svg"
        elif play_state == "||":
            state_pic = "dvr_pause.svg"
        elif play_state == "Stop":
            state_pic = "dvr_stop.svg"
        elif play_state == "End":
            state_pic = "dvr_stop.svg"
            factor = _("End")
        elif play_state.startswith(">>"):
            factor = play_state.split(" ")[1]
            state_pic = "dvr_forward.svg"
        elif play_state.startswith("<<"):
            state_pic = "dvr_backward.svg"
            factor = play_state.split(" ")[1]
        elif play_state.startswith("/"):
            state_pic = "dvr_play.svg"
            factor = "1" + play_state + "x"

        self.pvr_state_dialog["state_pic"].instance.setPixmap(LoadPixmap(getSkinPath("images/dvr_controls/" + state_pic), cached=False, size=eSize(100, 100)))
        self.pvr_state_dialog["state"].setText(factor)

        logger.debug("seekstate: %s, show_state_pic: %s", self.seekstate, self.show_state_pic)
        if not self.show_state_pic or (not config.usage.show_infobar_on_skip.value and self.seekstate in (self.SEEK_STATE_PLAY, self.SEEK_STATE_STOP)):
            self.pvr_state_dialog.hide()
        else:
            if self.show_state_pic:
                self.mayShow()

    def delPvrState(self):
        logger.info("...")
        self.onPlayStateChanged = self.on_play_state_changed[:]
        self.session.deleteDialog(self.pvr_state_dialog)
        self.pvr_state_dialog = None

    def mayShow(self):
        logger.info("execing: %s", self.execing)
        if self.execing and self.seekstate != self.SEEK_STATE_PLAY:
            self.pvr_state_dialog.show()
