#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2019 by dream-alpha
#
# In case of reuse of this source code please do not remove this copyright.
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	For more information on the GNU General Public License see:
#	<http://www.gnu.org/licenses/>.

import os
from __init__ import _
from Components.config import config, getConfigListEntry, configfile, ConfigText, ConfigPassword
from Components.Button import Button
from Components.Sources.StaticText import StaticText
from Screens.Screen import Screen
from Screens.LocationBox import LocationBox
from Screens.MessageBox import MessageBox
from Screens.VirtualKeyBoard import VirtualKeyBoard
from Components.ActionMap import ActionMap
from enigma import eTimer, ePoint
from Components.ConfigList import ConfigListScreen
from Screens.Standby import TryQuitMainloop
from Tools.Directories import resolveFilename, SCOPE_PLUGINS
from Version import VERSION
from ConfigInit import ConfigInit


class ConfigScreen(ConfigInit, ConfigListScreen, Screen, object):
	def __init__(self, session, sections="cockpit"):
		ConfigInit.__init__(self)
		self.sections = sections
		Screen.__init__(self, session)
		self.skinName = ["MDCConfigScreen"]

		self["actions"] = ActionMap(
			["OkCancelActions", "MDCActions"],
			{
				"exit": self.keyCancel,
				"red": self.keyCancel,
				"green": self.keySaveNew,
				"yellow": self.loadDefaultSettings,
				"nextBouquet": self.bouquetPlus,
				"previousBouquet": self.bouquetMinus,
			},
			-2  # higher priority
		)

		self["VirtualKB"] = ActionMap(
			["VirtualKeyboardActions"],
			{
				"showVirtualKeyboard": self.keyText,
			},
			-2  # higher priority
		)

		self["VirtualKB"].setEnabled(False)

		self["key_red"] = Button(_("Cancel"))
		self["key_green"] = Button(_("Save"))
		self["key_yellow"] = Button(_("Defaults"))
		self["key_blue"] = Button("")
		self["help"] = StaticText()

		self.list = []
		self.config_list = []
		ConfigListScreen.__init__(self, self.list, session=self.session, on_change=self.changedEntry)
		self.needs_restart_flag = False
		self.defineConfig()
		self.createConfig()

		self.reloadTimer = eTimer()
		self.reloadTimer_conn = self.reloadTimer.timeout.connect(self.createConfig)

		# Override selectionChanged because our config tuples have a size bigger than 2
		def selectionChanged():
			current = self["config"].getCurrent()
			if self["config"].current != current:
				if self["config"].current:
					try:
						self["config"].current[1].onDeselect()
					except Exception:
						pass
				if current:
					try:
						current[1].onSelect()
					except Exception:
						pass
				self["config"].current = current
			for x in self["config"].onSelectionChanged:
				try:
					x()
				except Exception:
					pass
		self["config"].selectionChanged = selectionChanged
		self["config"].onSelectionChanged.append(self.updateHelp)
		self["config"].onSelectionChanged.append(self.handleInputHelpers)

	def defineConfig(self):
		self.section = 400 * "¯"
		#        config list entry
		#                                                                   , config element
		#                                                                   ,                                                       , function called on save
		#                                                                   ,                                                       ,                       , function called if user has pressed OK
		#                                                                   ,                                                       ,                       ,                       , usage setup level from E2
		#                                                                   ,                                                       ,                       ,                       ,   0: simple+
		#                                                                   ,                                                       ,                       ,                       ,   1: intermediate+
		#                                                                   ,                                                       ,                       ,                       ,   2: expert+
		#                                                                   ,                                                       ,                       ,                       ,       , depends on relative parent entries
		#                                                                   ,                                                       ,                       ,                       ,       ,   parent config value < 0 = true
		#                                                                   ,                                                       ,                       ,                       ,       ,   parent config value > 0 = false
		#                                                                   ,                                                       ,                       ,                       ,       ,             , context sensitive help text
		#                                                                   ,                                                       ,                       ,                       ,       ,             ,
		#        0                                                          , 1                                                     , 2                     , 3                     , 4     , 5           , 6
		if self.sections == "cockpit":
			self.MDCConfig1 = [
				(self.section                                       , _("PLUGIN")                                           , None                  , None                  , 0     , []          , ""),
				(_("About")                                         , config.plugins.mediacockpit.fake_entry                , None                  , self.showInfo         , 0     , []          , _("HELP About")),
				(_("Start plugin with key")                         , config.plugins.mediacockpit.launch_key                , self.needsRestart     , None                  , 0     , []          , _("Help Start plugin with key")),
				(self.section                                       , _("COCKPIT")                                          , None                  , None                  , 0     , []          , ""),
				(_("Start with home directory")                     , config.plugins.mediacockpit.start_home_dir            , None                  , None                  , 0     , []          , _("Help Start into home directory")),
				(_("Home directory")                                , config.plugins.mediacockpit.home_dir                  , self.validatePath     , self.openLocationBox  , 0     , [-1]        , _("Help Home directory")),
				(_("Sort")                                          , config.plugins.mediacockpit.sort                      , None                  , None                  , 0     , []          , _("Help Sort")),
				(_("Sort across directories")                       , config.plugins.mediacockpit.sort_across_dirs          , None                  , None                  , 0     , []          , _("Help Sort across directories")),
				(_("TV playback in background")                     , config.plugins.mediacockpit.tv_background             , None                  , None                  , 0     , []          , _("Help TV playback in background")),
				(_("Show directory up tile")                        , config.plugins.mediacockpit.show_goup_tile            , None                  , None                  , 0     , []          , _("Help Show directory up tile")),
				(_("Tile foreground color")                         , config.plugins.mediacockpit.normal_foreground_color   , None                  , None                  , 0     , []          , _("Help Tile foreground color")),
				(_("Tile background color")                         , config.plugins.mediacockpit.normal_background_color   , None                  , None                  , 0     , []          , _("Help Tile background color")),
				(_("Tile selection foreground color")               , config.plugins.mediacockpit.selection_foreground_color, None                  , None                  , 0     , []          , _("Help Tile selection foreground color")),
				(_("Tile selection background color")               , config.plugins.mediacockpit.selection_background_color, None                  , None                  , 0     , []          , _("Help Tile selection background color")),
				(_("Tile selection size offset")                    , config.plugins.mediacockpit.selection_size_offset     , None                  , None                  , 0     , []          , _("Help Tile selection size offset")),
				(_("Tile selection font offset")                    , config.plugins.mediacockpit.selection_font_offset     , None                  , None                  , 0     , []          , _("Help Tile selection font offset")),
				(_("Tile selection frame")                          , config.plugins.mediacockpit.frame                     , None                  , None                  , 0     , []          , _("Help Tile selection frame")),
				(_("Tile selection frame color")                    , config.plugins.mediacockpit.selection_frame_color     , None                  , None                  , 0     , [-1]        , _("Help Tile selection frame color")),
				(_("Create thumbnails")                             , config.plugins.mediacockpit.create_thumbnails         , None                  , None                  , 0     , []          , _("Help Create thumbnails")),
				(_("Show detailed loading info")                    , config.plugins.mediacockpit.show_loading_details      , None                  , None                  , 0     , []          , _("Help Show detailed loading info")),
				(self.section                                       , _("VIDEO")                                            , None                  , None                  , 2     , []          , ""),
				(_("Show info bar")                                  , config.plugins.mediacockpit.show_movie_infobar       , None                  , None                  , 0     , []          , _("Help Show movie info bar")),
				(self.section                                       , _("PLAYLIST")                                         , None                  , None                  , 2     , []          , ""),
				(_("Recurse directories")                           , config.plugins.mediacockpit.recurse_dirs              , None                  , None                  , 0     , []          , _("Help Recurse directories")),
				(self.section                                       , _("DEBUG")                                            , None                  , None                  , 2     , []          , ""),
				(_("Debug log")                                     , config.plugins.mediacockpit.debug                     , None                  , self.setDebugMode     , 2     , []          , _("Help Debug")),
				(_("Log file path")                                 , config.plugins.mediacockpit.debug_log_path            , self.validatePath     , self.openLocationBox  , 2     , [-1]        , _("Help Log file path")),
			]

		if self.sections in ["cockpit", "picture"]:
			self.MDCConfig2 = [
				(self.section                                       , _("PICTURE")                                          , None                  , None                  , 0     , []          , ""),
				(_("Foreground color")                              , config.plugins.mediacockpit.picture_foreground        , None                  , None                  , 0     , []          , _("Help Foreground color")),
				(_("Background color")                              , config.plugins.mediacockpit.picture_background        , None                  , None                  , 0     , []          , _("Help Background color")),
				(_("Show info bar")                                 , config.plugins.mediacockpit.show_picture_infobar      , None                  , None                  , 0     , []          , _("Help Show picture info bar")),
				(self.section                                       , _("SLIDESHOW")                                        , None                  , None                  , 0     , []          , ""),
				(_("Duration")                                      , config.plugins.mediacockpit.slideshow_duration        , None                  , None                  , 0     , []          , _("Help Duration")),
				(_("Animation")                                     , config.plugins.mediacockpit.animation                 , None                  , None                  , 0     , []          , _("Help Animation")),
				(_("Endless loop")                                  , config.plugins.mediacockpit.slideshow_loop            , None                  , None                  , 0     , []          , _("Help Endless loop")),
			]

	def handleInputHelpers(self):
		self["VirtualKB"].setEnabled(False)
		if self["config"].getCurrent():
			if isinstance(self["config"].getCurrent()[1], (ConfigPassword, ConfigText)):
				self["VirtualKB"].setEnabled(True)
				if hasattr(self, "HelpWindow"):
					if self["config"].getCurrent()[1].help_window.instance:
						helpwindowpos = self["HelpWindow"].getPosition()
						self["config"].getCurrent()[1].help_window.instance.move(ePoint(helpwindowpos[0], helpwindowpos[1]))

	def keyText(self):
		self.session.openWithCallback(self.VirtualKeyBoardCallback, VirtualKeyBoard, title=self["config"].getCurrent()[0], text=self["config"].getCurrent()[1].getValue())

	def VirtualKeyBoardCallback(self, callback=None):
		if callback:
			self["config"].getCurrent()[1].setValue(callback)
			self["config"].invalidate(self["config"].getCurrent())

	def keySave(self):
		for x in self["config"].list:
			if len(x) > 1:
				x[1].save()
		self.close()

	def cancelConfirm(self, answer):
		if answer:
			for x in self["config"].list:
				if len(x) > 1:
					x[1].cancel()
			self.close()

	def keyCancel(self):
		if self["config"].isChanged():
			self.session.openWithCallback(self.cancelConfirm, MessageBox, _("Really close without saving settings?"))
		else:
			self.close()

	def bouquetPlus(self):
		self["config"].jumpToPreviousSection()

	def bouquetMinus(self):
		self["config"].jumpToNextSection()

	def createConfig(self):
		self.list = []
		if self.sections == "cockpit":
			self.config_list = self.MDCConfig1
		elif self.sections == "picture":
			self.config_list = self.MDCConfig2
		else:
			self.config_list = []

		for i, conf in enumerate(self.config_list):
			# 0 entry text
			# 1 variable
			# 2 validation
			# 3 pressed ok
			# 4 setup level
			# 5 parent entries
			# 6 help text
			# Config item must be valid for current usage setup level
			if config.usage.setup_level.index >= conf[4]:
				# Parent entries must be true
				for parent in conf[5]:
					if parent < 0:
						if not self.config_list[i + parent][1].value:
							break
					elif parent > 0:
						if self.config_list[i - parent][1].value:
							break
				else:
					# Loop fell through without a break
					if conf[0] == self.section:
						if len(self.list) > 1:
							self.list.append(getConfigListEntry("", config.plugins.mediacockpit.fake_entry, None, None, 0, [], ""))
						if conf[1] == "":
							self.list.append(getConfigListEntry("<DUMMY CONFIGSECTION>",))
						else:
							self.list.append(getConfigListEntry(conf[1],))
					else:
						self.list.append(getConfigListEntry(conf[0], conf[1], conf[2], conf[3], conf[4], conf[5], conf[6]))
		self["config"].setList(self.list)
		self.setTitle(_("Setup"))

	def loadDefaultSettings(self):
		self.session.openWithCallback(
			self.loadDefaultSettingsCallback,
			MessageBox,
			_("Loading default settings will overwrite all settings, really load them?"),
			MessageBox.TYPE_YESNO
		)

	def loadDefaultSettingsCallback(self, answer):
		if answer:
			# Refresh is done implicitly on change
			for conf in self.config_list:
				if len(conf) > 1 and conf[0] != self.section:
					conf[1].value = conf[1].default
			self.createConfig()

	def changedEntry(self, _addNotifier=None):
		if self.reloadTimer.isActive():
			self.reloadTimer.stop()
		self.reloadTimer.start(50, True)

	def updateHelp(self):
		cur = self["config"].getCurrent()
		self["help"].text = (cur[6] if cur else "")

	def dirSelected(self, res):
		if res:
			res = os.path.normpath(res)
			self["config"].getCurrent()[1].value = res

	def keyOK(self):
		try:
			current = self["config"].getCurrent()
			if current and current[3]:
				current[3](current[1])
		except Exception:
			print("MDC-E: ConfigScreen: keyOK: couldn't execute function for: %s" % str(current[0]))

	def keySaveNew(self):
		for i, entry in enumerate(self.list):
			if len(entry) > 1:
				if entry[1].isChanged():
					if entry[2]:
						# execute value changed -function
						if not entry[2](entry[1]):
							# Stop exiting, user has to correct the config
							print("MDC-E: ConfigScreen: keySaveNew: function called on save failed")
							return
					# Check parent entries
					for parent in entry[5]:
						try:
							if self.list[i + parent][2]:
								# execute parent value changed -function
								if self.list[i + parent][2](self.config_list[i + parent][1]):
									# Stop exiting, user has to correct the config
									return
						except Exception as e:
							print("MDC-E: ConfigScreen: keySaveNew: i: %s, exception: %s" % (i, e))
							continue
					entry[1].save()
		configfile.save()

		if self.needs_restart_flag:
			self.restartGUI()
		else:
			self.close(True)

	def restartGUI(self):
		self.session.openWithCallback(self.restartGUIConfirmed, MessageBox, _("Some changes require a GUI restart") + "\n" + _("Restart GUI now?"), MessageBox.TYPE_YESNO)

	def restartGUIConfirmed(self, answer):
		if answer:
			self.session.open(TryQuitMainloop, 3)
		else:
			self.close(True)

	def setDebugMode(self, element):
		#print("MDC: ConfigScreen: setDebugMode: element: %s" % element.value)
		py_files = resolveFilename(SCOPE_PLUGINS, "Extensions/MediaCockpit/*.py")
		if element.value:
			cmd = "sed -i 's/#print(\"MDC:/print(\"MDC:/g' " + py_files
			#print("MDC: ConfigScreen: setDebugMode: cmd: %s" % cmd)
			os.system(cmd)
		else:
			cmd = "sed -i 's/print(\"MDC:/#print(\"MDC:/g' " + py_files
			#print("MDC: ConfigScreen: setDebugMode: cmd: %s" % cmd)
			os.system(cmd)
			cmd = "sed -i 's/##print(\"MDC:/#print(\"MDC:/g' " + py_files
			#print("MDC: ConfigScreen: setDebugMode: cmd: %s" % cmd)
			os.system(cmd)
		self.needsRestart()

	def needsRestart(self, _element=None):
		self.needs_restart_flag = True
		return True

	def openLocationBox(self, element):
		if element:
			path = os.path.normpath(element.value)
			self.session.openWithCallback(
				self.dirSelected,
				LocationBox,
				windowTitle=_("Select directory"),
				text=_("Select directory"),
				currDir=path + "/",
				bookmarks=config.plugins.mediacockpit.media_dirs,
				autoAdd=False,
				editDir=True,
				inhibitDirs=["/bin", "/boot", "/dev", "/etc", "/lib", "/proc", "/sbin", "/sys", "/var"],
				minFree=100
			)

	def showInfo(self, _element=None):
		self.session.open(MessageBox, "MediaCockpit" + ": Version " + VERSION, MessageBox.TYPE_INFO)

	def validatePath(self, element):
		element.value = os.path.normpath(element.value)
		if not os.path.exists(element.value):
			self.session.open(MessageBox, _("Path does not exist") + ": " + str(element.value), MessageBox.TYPE_ERROR)
			return False
		return True
