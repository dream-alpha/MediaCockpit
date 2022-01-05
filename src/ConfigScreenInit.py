#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2023 by dream-alpha
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


from Components.config import config
from Screens.MessageBox import MessageBox
from .Debug import logger
from .__init__ import _
from .Version import VERSION


class ConfigScreenInit():
	def __init__(self, session):
		self.session = session
		self.section = 400 * "¯"

		#        config list entry
		#                                                           , config element
		#                                                           ,                                                               , function called on save
		#                                                           ,                                                               ,                       , function called if user has pressed OK
		#                                                           ,                                                               ,                       ,                       , usage setup level from E2
		#                                                           ,                                                               ,                       ,                       ,   0: simple+
		#                                                           ,                                                               ,                       ,                       ,   1: intermediate+
		#                                                           ,                                                               ,                       ,                       ,   2: expert+
		#                                                           ,                                                               ,                       ,                       ,       , depends on relative parent entries
		#                                                           ,                                                               ,                       ,                       ,       ,   parent config value < 0 = true
		#                                                           ,                                                               ,                       ,                       ,       ,   parent config value > 0 = false
		#                                                           ,                                                               ,                       ,                       ,       ,             , context sensitive help text
		#                                                           ,                                                               ,                       ,                       ,       ,             ,
		#        0                                                  , 1                                                             , 2                     , 3                     , 4     , 5           , 6
		self.config_list = [
			(self.section                                       , _("COCKPIT")                                                  , None                  , None                  , 0     , []          , ""),
			(_("Start with top level favorites")                , config.plugins.mediacockpit.start_home_dir                    , None                  , None                  , 0     , []          , _("Should the plugin load the top level favorite directories or the directory that was used last?")),
			(_("Activate File Cache")                           , config.plugins.mediacockpit.cache                             , None                  , None                  , 0     , []          , _("Activate the media file cache for faster loading.")),
			(_("Sort")                                          , config.plugins.mediacockpit.sort                              , None                  , None                  , 0     , []          , _("Select the list sort mode.")),
			(_("Sort across directories")                       , config.plugins.mediacockpit.sort_across_dirs                  , None                  , None                  , 0     , []          , _("Should directories be sorted recursively?")),
			(_("Show parent directory tile")                    , config.plugins.mediacockpit.show_dirup_tile                   , None                  , None                  , 0     , []          , _("Should a tile be displayed for navigation to the parent directory?")),
			(_("Tile foreground color")                         , config.plugins.mediacockpit.normal_foreground_color           , self.needsRestart     , None                  , 0     , []          , _("Select the tile foreground color.")),
			(_("Tile background color")                         , config.plugins.mediacockpit.normal_background_color           , self.needsRestart     , None                  , 0     , []          , _("Select the tile background color.")),
			(_("Tile selection foreground color")               , config.plugins.mediacockpit.selection_foreground_color        , self.needsRestart     , None                  , 0     , []          , _("Select the tile selection foreground color.")),
			(_("Tile selection background color")               , config.plugins.mediacockpit.selection_background_color        , self.needsRestart     , None                  , 0     , []          , _("Select the tile selection background color.")),
			(_("Tile selection size offset")                    , config.plugins.mediacockpit.selection_size_offset             , None                  , None                  , 0     , []          , _("Select the tile selection size offset.")),
			(_("Tile selection font offset")                    , config.plugins.mediacockpit.selection_font_offset             , None                  , None                  , 0     , []          , _("Select the tile selection font offset.")),
			(_("Tile selection frame")                          , config.plugins.mediacockpit.frame                             , None                  , None                  , 0     , []          , _("Should a tile selection frame be displayed?")),
			(_("Tile selection frame color")                    , config.plugins.mediacockpit.selection_frame_color             , self.needsRestart     , None                  , 0     , [-1]        , _("Select the tile selection frame color.")),
			(_("Create thumbnails")                             , config.plugins.mediacockpit.create_thumbnails                 , None                  , None                  , 0     , []          , _("Should thumbnails be created automatically?")),
			(_("Show detailed loading info")                    , config.plugins.mediacockpit.show_loading_details              , None                  , None                  , 0     , []          , _("Should detailed loading info be shown?")),
			(self.section                                       , _("SLIDESHOW")                                                , None                  , None                  , 0     , []          , ""),
			(_("Duration")                                      , config.plugins.mediacockpit.slideshow_duration                , None                  , None                  , 0     , []          , _("Select the duration for the display of a slide.")),
			(_("Animation")                                     , config.plugins.mediacockpit.animation                         , None                  , None                  , 0     , []          , _("Which animation should be used for slide transistions?")),
			(_("Endless loop")                                  , config.plugins.mediacockpit.slideshow_loop                    , None                  , None                  , 0     , []          , _("Should slideshows be run in an endless loop?")),
			(self.section                                       , _("PLAYLIST")                                                 , None                  , None                  , 0     , []          , ""),
			(_("Recurse directories")                           , config.plugins.mediacockpit.recurse_dirs                      , None                  , None                  , 0     , []          , _("Should directories be loaded recursively?")),
			(self.section                                       , _("PICTURE")                                                  , None                  , None                  , 0     , []          , ""),
			(_("Foreground color")                              , config.plugins.mediacockpit.picture_foreground                , self.needsRestart     , None                  , 0     , []          , _("Select the forground color of icons.")),
			(_("Background color")                              , config.plugins.mediacockpit.picture_background                , self.needsRestart     , None                  , 0     , []          , _("Select the background color for icons.")),
			(self.section                                       , _("VIDEO")                                                    , None                  , None                  , 2     , []          , ""),
			(_("Resume video at last position")                 , config.plugins.mediacockpit.movie_resume_at_last_pos          , None                  , None                  , 1     , []          , _("Select whether video should be resumed at last stop position.")),
			(_("Video start at")                                , config.plugins.mediacockpit.movie_start_position              , None                  , None                  , 1     , []          , _("Select at which position video is started at.")),
			(_("Date format")                                   , config.plugins.mediacockpit.movie_date_format                 , None                  , None                  , 0     , []          , _("Select the date format.")),
			(self.section                                       , _("MUSIC")                                                    , None                  , None                  , 0     , []          , ""),
			(_("Gapless playback")                              , config.plugins.mediacockpit.gapless                           , None                  , None                  , 0     , []          , _("Should gapless playback be used?")),
			(_("Alsasink")                                      , config.plugins.mediacockpit.alsasink                          , None                  , None                  , 0     , []          , _("Should the GStreamer Alsasink decoder be used?")),
			(_("Cover download path")                           , config.plugins.mediacockpit.cover_download_path               , self.validatePath     , self.openLocationBox  , 0     , []          , _("Select the path for cover downloads.")),
			(self.section                                       , _("DEBUG")                                                    , None                  , None                  , 2     , []          , ""),
			(_("Debug log")                                     , config.plugins.mediacockpit.debug_log_level                   , self.setLogLevel      , None                  , 2     , []          , _("Should a debug log be activated?")),
			(_("Log file path")                                 , config.plugins.mediacockpit.debug_log_path                    , self.validatePath     , self.openLocationBox  , 2     , [-1]        , _("Select the path for a log file.")),
		]

	@staticmethod
	def save(_conf):
		logger.debug("...")

	def needsRestart(self, _element):
		return

	def validatePath(self, _element):
		return

	def openLocationBox(self, _element):
		return

	def setLogLevel(self, _element):
		return

	def showInfo(self, _element=None):
		self.session.open(MessageBox, "MediaCockpit" + ": Version " + VERSION, MessageBox.TYPE_INFO)
