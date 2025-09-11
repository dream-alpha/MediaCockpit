#!/usr/bin/python
# encoding: utf-8
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


from enigma import eConsoleAppContainer


class ConsoleAppContainer():

    def __init__(self, callback=None):
        self.callback = callback
        self.container = None

    def execute(self, cmd):
        self.container = eConsoleAppContainer()
        self.container_appClosed_conn = self.container.appClosed.connect(
            self.__callback)
        self.container.execute(cmd)

    def __callback(self, _ret_val=None):
        self.container = None
        if self.callback is not None:
            self.callback()

    def kill(self):
        if self.container is not None:
            self.container.kill()
            self.container = None
