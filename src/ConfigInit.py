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
from skin import colorNames
from Components.config import config, ConfigSet, ConfigDirectory, ConfigInteger, ConfigText, ConfigSelection, ConfigYesNo, ConfigSubsection, ConfigNothing, NoSave
from .__init__ import _
from .Debug import logger, log_levels, initLogging


choices_date = [
    ("%d.%m.%Y", _("DD.MM.YYYY")),
    ("%a %d.%m.%Y", _("WD DD.MM.YYYY")),

    ("%d.%m.%Y %H:%M", _("DD.MM.YYYY HH:MM")),
    ("%a %d.%m.%Y %H:%M", _("WD DD.MM.YYYY HH:MM")),

    ("%d.%m. %H:%M", _("DD.MM. HH:MM")),
    ("%a %d.%m. %H:%M",	_("WD DD.MM. HH:MM")),

    ("%Y/%m/%d", _("YYYY/MM/DD")),
    ("%a %Y/%m/%d", _("WD YYYY/MM/DD")),

    ("%Y/%m/%d %H:%M", _("YYYY/MM/DD HH:MM")),
    ("%a %Y/%m/%d %H:%M", _("WD YYYY/MM/DD HH:MM")),

    ("%m/%d %H:%M", _("MM/DD HH:MM")),
    ("%a %m/%d %H:%M", _("WD MM/DD HH:MM"))
]


choices_cover_downloader = [
    ("lastfm", "LastFM"),
    ("none", _("None")),
]


sort_modes = {
    "0": (("date", False), _("Date sort down")),
    "1": (("date", True), _("Date sort up")),
    "2": (("alpha", False), _("Alpha sort up")),
    "3": (("alpha", True), _("Alpha sort down")),
}


choices_sort = [(k, v[1]) for k, v in list(sort_modes.items())]


choices_color = []
for key in list(colorNames.keys()):
    choices_color.append((key, _(key)))


ext_slideshow_animations = [
    ("0", _("blinds")),
    ("1", _("rotate")),
    ("2", _("circular waves")),
    ("3", _("door")),
    ("4", _("dice")),
    ("5", _("checkerboard")),
    ("6", _("shutter")),
    ("7", _("waves")),
    ("8", _("windmill")),
    ("9", _("earthquake")),
    ("10", _("crossfade")),
    ("11", _("random"))
]


int_slideshow_animations = [
    ("12", _("Crossfade fast")),
    ("13", _("Crossfade slow")),
    ("14", _("Crossfade accelerated")),
    ("15", _("Crossfade regular"))
]


def initBookmarks():
    logger.info("...")
    bookmarks = []
    adir = "/media"
    for afile in os.listdir(adir):
        path = os.path.join(adir, afile)
        bookmarks.append(path)
    if not bookmarks:
        bookmarks.append(adir)
    logger.debug("bookmarks: %s", bookmarks)
    return bookmarks


class ConfigInit():

    def __init__(self):
        logger.debug("...")
        choices_slideshow_animation = ext_slideshow_animations + int_slideshow_animations

        config.plugins.mediacockpit = ConfigSubsection()
        config.plugins.mediacockpit.fake_entry = NoSave(ConfigNothing())
        config.plugins.mediacockpit.sort = ConfigSelection(
            default="2", choices=choices_sort)
        config.plugins.mediacockpit.last_path = ConfigText(default="")
        config.plugins.mediacockpit.start_home_dir = ConfigYesNo(default=True)
        config.plugins.mediacockpit.frame = ConfigYesNo(default=True)
        config.plugins.mediacockpit.create_thumbnails = ConfigYesNo(
            default=True)
        config.plugins.mediacockpit.thumbnail_size_width = ConfigInteger(
            default=0)
        config.plugins.mediacockpit.thumbnail_size_height = ConfigInteger(
            default=0)
        config.plugins.mediacockpit.show_dirup_tile = ConfigYesNo(default=True)
        config.plugins.mediacockpit.selection_size_offset = ConfigInteger(
            default=10, limits=(0, 50))
        config.plugins.mediacockpit.selection_font_offset = ConfigInteger(
            default=2, limits=(0, 10))
        config.plugins.mediacockpit.normal_background_color = ConfigSelection(
            default="#20294071", choices=choices_color + [("#20294071", _("default"))])
        config.plugins.mediacockpit.selection_background_color = ConfigSelection(
            default="#204176b6", choices=choices_color + [("#204176b6", _("default"))])
        config.plugins.mediacockpit.normal_foreground_color = ConfigSelection(
            default="#eeeeee", choices=choices_color + [("#eeeeee", _("default"))])
        config.plugins.mediacockpit.selection_foreground_color = ConfigSelection(
            default="#ffffff", choices=choices_color + [("#ffffff", _("default"))])
        config.plugins.mediacockpit.selection_frame_color = ConfigSelection(
            default="#b3b3b9", choices=choices_color + [("#b3b3b9", _("default"))])
        config.plugins.mediacockpit.slideshow_loop = ConfigYesNo(default=False)
        config.plugins.mediacockpit.slideshow_duration = ConfigInteger(
            default=5, limits=(3, 30))
        config.plugins.mediacockpit.animation = ConfigSelection(
            default="10", choices=choices_slideshow_animation)
        config.plugins.mediacockpit.recurse_dirs = ConfigYesNo(default=True)
        config.plugins.mediacockpit.sort_across_dirs = ConfigYesNo(
            default=False)
        config.plugins.mediacockpit.picture_background = ConfigSelection(
            default="black", choices=choices_color)
        config.plugins.mediacockpit.picture_foreground = ConfigSelection(
            default="foreground", choices=choices_color)
        config.plugins.mediacockpit.debug_log_level = ConfigSelection(
            default="DEBUG", choices=list(log_levels.keys()))
        config.plugins.mediacockpit.non_standard_decoder = ConfigYesNo(
            default=True)
        config.plugins.mediacockpit.cover_downloader = ConfigSelection(
            default="lastfm", choices=choices_cover_downloader)
        config.plugins.mediacockpit.cover_download_path = ConfigDirectory(
            default="/data/music/covers")
        config.plugins.mediacockpit.database_directory = ConfigDirectory(
            default="/etc/enigma2")
        config.plugins.mediacockpit.gapless = ConfigYesNo(default=True)
        config.plugins.mediacockpit.alsasink = ConfigYesNo(default=True)
        config.plugins.mediacockpit.movie_resume_at_last_pos = ConfigYesNo(
            default=False)
        config.plugins.mediacockpit.movie_start_position = ConfigSelection(default="beginning", choices=[(
            "beginning", _("beginning")), ("first_mark", _("first mark")), ("event_start", _("event start"))])
        config.plugins.mediacockpit.movie_date_format = ConfigSelection(
            default="%d.%m.%Y %H:%M", choices=choices_date)
        config.plugins.mediacockpit.bookmarks = ConfigSet([], [])
        if not config.plugins.mediacockpit.bookmarks.value:
            config.plugins.mediacockpit.bookmarks.value = initBookmarks()
            config.plugins.mediacockpit.bookmarks.save()

        initLogging()
