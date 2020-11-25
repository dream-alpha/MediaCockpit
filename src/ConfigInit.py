#!/usr/bin/python
# coding=utf-8
#
# Copyright (C) 2018-2020 by dream-alpha
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

from __init__ import _
from skin import colorNames
from Components.config import config, ConfigDirectory, ConfigInteger, ConfigText, ConfigSelection, ConfigYesNo, ConfigSubsection, ConfigNothing, NoSave, ConfigLocations
from Components.Language import language
from Tools.ISO639 import ISO639Language


class Autoselect639Language(ISO639Language):

	def __init__(self):
		ISO639Language.__init__(self, self.TERTIARY)

	def getTranslatedChoicesDictAndSortedListAndDefaults(self):
		syslang = language.getLanguage()[:2]
		choices_dict = {}
		choices_list = []
		defaults = []
		for lang, id_list in self.idlist_by_name.iteritems():
			if syslang not in id_list and 'en' not in id_list:
				name = _(lang)
				short_id = sorted(id_list, key=len)[0]
				choices_dict[short_id] = name
				choices_list.append((short_id, name))
		choices_list.sort(key=lambda x: x[1])
		syslangname = _(self.name_by_shortid[syslang])
		choices_list.insert(0, (syslang, syslangname))
		choices_dict[syslang] = syslangname
		defaults.append(syslang)
		if syslang != "en":
			enlangname = _(self.name_by_shortid["en"])
			choices_list.insert(1, ("en", enlangname))
			choices_dict["en"] = enlangname
			defaults.append("en")
		return (choices_dict, choices_list, defaults)


def langList():
	iso639 = Autoselect639Language()
	newlist = iso639.getTranslatedChoicesDictAndSortedListAndDefaults()[1]
	#print("MDC: ConfigInit: langList: %s" % str(newlist))
	return newlist


def langListSel():
	iso639 = Autoselect639Language()
	newlist = iso639.getTranslatedChoicesDictAndSortedListAndDefaults()[0]
	return newlist


choices_launch_key = [
	("None",		_("No override")),
	("showMovies",		_("Video-button")),
	("showTv",		_("TV-button")),
	("showRadio",		_("Radio-button")),
	("openQuickbutton",	_("Quick-button")),
	("startTimeshift",	_("Timeshift-button")),
]


choices_date = [
	("%d.%m.%Y",		_("DD.MM.YYYY")),
	("%a %d.%m.%Y",		_("WD DD.MM.YYYY")),

	("%d.%m.%Y %H:%M",	_("DD.MM.YYYY HH:MM")),
	("%a %d.%m.%Y %H:%M",	_("WD DD.MM.YYYY HH:MM")),

	("%d.%m. %H:%M",	_("DD.MM. HH:MM")),
	("%a %d.%m. %H:%M",	_("WD DD.MM. HH:MM")),

	("%Y/%m/%d",		_("YYYY/MM/DD")),
	("%a %Y/%m/%d",		_("WD YYYY/MM/DD")),

	("%Y/%m/%d %H:%M",	_("YYYY/MM/DD HH:MM")),
	("%a %Y/%m/%d %H:%M",	_("WD YYYY/MM/DD HH:MM")),

	("%m/%d %H:%M",		_("MM/DD HH:MM")),
	("%a %m/%d %H:%M",	_("WD MM/DD HH:MM"))
]


choices_cover_downloader = [
	("lastfm", 		"LastFM"),
	("google", 		"Google"),
	("none", 		_("None")),
]

sort_modes = {
	"0": (("date", False),	_("Date sort down")),
	"1": (("date", True), 	_("Date sort up")),
	"2": (("alpha", False),	_("Alpha sort up")),
	"3": (("alpha", True),	_("Alpha sort down")),
}


choices_sort = [(k, v[1]) for k, v in sort_modes.items()]


choices_color = []
for key in colorNames.iterkeys():
	choices_color.append((key, _(key)))


ext_slideshow_animations = [
	("0", _("blinds")), ("1", _("rotate")), ("2", _("circular waves")), ("3", _("door")),
	("4", _("dice")), ("5", _("checkerboard")), ("6", _("shutter")), ("7", _("waves")), ("8", _("windmill")),
	("9", _("earthquake")), ("10", _("crossfade")), ("11", _("random"))
]


int_slideshow_animations = [
	("12", _("Crossfade fast")), ("13", _("Crossfade slow")),
	("14", _("Crossfade accelerated")), ("15", _("Crossfade regular"))
]


class ConfigInit():

	config = None

	def __init__(self):
		#print("MDC: ConfigInit: __init__")

		try:
			from Components.MerlinPictureViewerWidget import MerlinPictureViewer  # noqa: F401, pylint: disable=W0611,W0612
			choices_slideshow_animation = ext_slideshow_animations + int_slideshow_animations
		except Exception:
			choices_slideshow_animation = int_slideshow_animations

		config.plugins.mediacockpit                            = ConfigSubsection()
		config.plugins.mediacockpit.sort                       = ConfigSelection(default="2", choices=choices_sort)
		config.plugins.mediacockpit.last_path                  = ConfigText(default="/media")
		config.plugins.mediacockpit.start_home_dir             = ConfigYesNo(default=False)
		config.plugins.mediacockpit.home_dir                   = ConfigText(default="/media", fixed_size=False, visible_width=35)
		config.plugins.mediacockpit.frame                      = ConfigYesNo(default=True)
		config.plugins.mediacockpit.create_thumbnails          = ConfigYesNo(default=True)
		config.plugins.mediacockpit.show_goup_tile             = ConfigYesNo(default=True)
		config.plugins.mediacockpit.selection_size_offset      = ConfigInteger(default=10, limits=(0, 50))
		config.plugins.mediacockpit.selection_font_offset      = ConfigInteger(default=2, limits=(1, 10))
		config.plugins.mediacockpit.normal_background_color    = ConfigSelection(default="#20294071", choices=choices_color + [("#20294071", _("default"))])
		config.plugins.mediacockpit.selection_background_color = ConfigSelection(default="#204176b6", choices=choices_color + [("#204176b6", _("default"))])
		config.plugins.mediacockpit.normal_foreground_color    = ConfigSelection(default="#eeeeee", choices=choices_color + [("#eeeeee", _("default"))])
		config.plugins.mediacockpit.selection_foreground_color = ConfigSelection(default="#ffffff", choices=choices_color + [("#ffffff", _("default"))])
		config.plugins.mediacockpit.selection_frame_color      = ConfigSelection(default="#b3b3b9", choices=choices_color + [("#b3b3b9", _("default"))])
		config.plugins.mediacockpit.slideshow_loop             = ConfigYesNo(default=False)
		config.plugins.mediacockpit.slideshow_duration         = ConfigInteger(default=5, limits=(3, 30))
		config.plugins.mediacockpit.animation                  = ConfigSelection(default="10", choices=choices_slideshow_animation)
		config.plugins.mediacockpit.recurse_dirs               = ConfigYesNo(default=True)
		config.plugins.mediacockpit.sort_across_dirs           = ConfigYesNo(default=False)
		config.plugins.mediacockpit.picture_background         = ConfigSelection(default="black", choices=choices_color)
		config.plugins.mediacockpit.picture_foreground         = ConfigSelection(default="foreground", choices=choices_color)
		config.plugins.mediacockpit.show_loading_details       = ConfigYesNo(default=True)
		config.plugins.mediacockpit.launch_key                 = ConfigSelection(default="None", choices=choices_launch_key)
		config.plugins.mediacockpit.media_dirs                 = ConfigLocations(default=["/media"])
		config.plugins.mediacockpit.fake_entry                 = NoSave(ConfigNothing())
		config.plugins.mediacockpit.debug                      = ConfigYesNo(default=False)
		config.plugins.mediacockpit.debug_log_path             = ConfigText(default="/media/hdd", fixed_size=False, visible_width=35)
		# MDCMusicPlayer
		config.plugins.mediacockpit.non_standard_decoder       = ConfigYesNo(default=True)
		config.plugins.mediacockpit.cover_downloader           = ConfigSelection(default="lastfm", choices=choices_cover_downloader)
		config.plugins.mediacockpit.cover_download_path        = ConfigDirectory(default="/data/music/covers")
		config.plugins.mediacockpit.gapless                    = ConfigYesNo(default=True)
		config.plugins.mediacockpit.alsasink                   = ConfigYesNo(default=True)

		config.plugins.mediacockpit.sublang1                   = ConfigSelection(default=language.lang[language.getActiveLanguage()][0], choices=langList())
		config.plugins.mediacockpit.sublang2                   = ConfigSelection(default=language.lang[language.getActiveLanguage()][0], choices=langList())
		config.plugins.mediacockpit.sublang3                   = ConfigSelection(default=language.lang[language.getActiveLanguage()][0], choices=langList())
		config.plugins.mediacockpit.audlang1                   = ConfigSelection(default=language.lang[language.getActiveLanguage()][0], choices=langList())
		config.plugins.mediacockpit.audlang2                   = ConfigSelection(default=language.lang[language.getActiveLanguage()][0], choices=langList())
		config.plugins.mediacockpit.audlang3                   = ConfigSelection(default=language.lang[language.getActiveLanguage()][0], choices=langList())
		config.plugins.mediacockpit.autosubs                   = ConfigYesNo(default=False)
		config.plugins.mediacockpit.autoaudio                  = ConfigYesNo(default=False)
		config.plugins.mediacockpit.autoaudio_ac3              = ConfigYesNo(default=False)

		config.plugins.mediacockpit.record_eof_zap             = ConfigSelection(default='1', choices=[('0', _("yes, without Message")), ('1', _("yes, with Message")), ('2', _("no"))])
		config.plugins.mediacockpit.movie_date_format          = ConfigSelection(default="%d.%m.%Y %H:%M", choices=choices_date)
		config.plugins.mediacockpit.movie_ignore_firstcuts     = ConfigYesNo(default=True)
		config.plugins.mediacockpit.movie_jump_first_mark      = ConfigYesNo(default=False)

		self.config = config
