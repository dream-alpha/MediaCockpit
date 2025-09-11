# coding=utf-8
#
# Copyright (C) 2018-2025 by dream-alpha
#:
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


from Components.ActionMap import ActionMap
from Components.Label import Label
from Components.Button import Button
from Components.Slider import Slider
from Screens.Screen import Screen
from .__init__ import _
from .Debug import logger
from .BoxUtils import dimmOSD


class FileProgress(Screen):

    def __init__(self, session):
        logger.debug("...")
        Screen.__init__(self, session)

        self["slider1"] = Slider(0, 100)

        self["status"] = Label("")
        self["name"] = Label("")
        self["operation"] = Label("")

        self["key_red"] = Button(_("Cancel"))
        self["key_green"] = Button(_("Close"))
        self["key_green"].hide()
        self["key_yellow"] = Button("")
        self["key_blue"] = Button(_("Hide"))

        self["actions"] = ActionMap(
            ["OkCancelActions", "ColorActions"],
            {"ok": self.exit, "cancel": self.exit, "red": self.cancel, "green": self.exit, "yellow": self.noop, "blue": self.toggleHide}
        )

        self.execution_list = []
        self.total_files = 0
        self.current_files = 0
        self.file_progress = 0
        self.file_name = ""
        self.status = ""
        self.request_cancel = False
        self.cancelled = False
        self.hidden = False

    def noop(self):
        return

    def cancel(self):
        if self.hidden:
            logger.debug("unhide")
            self.toggleHide()
        else:
            if self.cancelled or (self.current_files > self.total_files):
                self.exit()
            else:
                logger.debug("trigger")
                self.request_cancel = True
                self["key_red"].hide()
                self["key_blue"].hide()
                self["key_green"].hide()
                self.status = _("Cancelling, please wait") + " ..."

    def exit(self):
        logger.info("...")
        if self.hidden:
            logger.debug("unhide")
            self.toggleHide()
        else:
            if self.cancelled or (self.current_files > self.total_files):
                logger.debug("close")
                self.close()

    def toggleHide(self):
        if self.hidden:
            self.hidden = False
            dimmOSD(True)
        else:
            self.hidden = True
            dimmOSD(False)

    def updateProgress(self):
        logger.debug("file_name: %s, current_files: %s, total_files: %s, status: %s", self.file_name, self.current_files, self.total_files, self.status)
        current_files = self.current_files if self.current_files <= self.total_files else self.total_files
        msg = _("Processing") + ": " + str(current_files) + " " + _("of") + " " + str(self.total_files) + " ..."
        self["operation"].setText(msg)
        self["name"].setText(self.file_name)
        percent_complete = int(round(float(self.current_files - 1) / float(self.total_files) * 100)) if self.total_files > 0 else 0
        self["slider1"].setValue(percent_complete)
        self["status"].setText(self.status)

    def completionStatus(self):
        return _("Done") + "."

    def doFileOp(self, _afile):
        logger.error("should not be called at all, as overridden by child")

    def nextFileOp(self):
        logger.debug("...")

        self.current_files += 1
        if self.request_cancel and (self.current_files <= self.total_files):
            self.current_files -= 1
            if self.hidden:
                self.toggleHide()
            self["key_red"].hide()
            self["key_blue"].hide()
            self["key_green"].show()
            self.status = _("Cancelled") + "."
            self.cancelled = True
            self.updateProgress()
        else:
            if self.execution_list:
                afile = self.execution_list.pop(0)
                self.status = _("Please wait") + " ..."
                self.doFileOp(afile)
            else:
                logger.debug("done.")
                if self.hidden:
                    self.toggleHide()
                self["key_red"].hide()
                self["key_blue"].hide()
                self["key_green"].show()
                if self.cancelled:
                    self.status = _("Cancelled") + "."
                else:
                    self.status = self.completionStatus()
                self.updateProgress()
