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


from Screens.MessageBox import MessageBox
from .Version import PLUGIN, VERSION, COPYRIGHT, LICENSE
from .__init__ import _


def about(session):
    session.open(
        MessageBox,
        _("Plugin") + ": " + PLUGIN + "\n\n"
        + _("Version") + ": " + VERSION + "\n\n"
        + _("Copyright") + ": " + COPYRIGHT + "\n\n"
        + _("License") + ": " + LICENSE,
        MessageBox.TYPE_INFO
    )
