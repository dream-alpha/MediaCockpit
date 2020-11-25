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


import re
from urllib import quote
from Cover import Cover


class CoverGoogle(Cover):

	def __init__(self, download_dir, coverDownloadFinished, coverDownloadFailed):
		#print("MDC: CoverGoogle: __init__: download_dir: %s" % download_dir)
		Cover.__init__(self, download_dir, coverDownloadFinished, coverDownloadFailed)

	def determineContentURL(self, artist, album, title):
		if artist and album:
			search = quote("%s+%s" % (album, artist))
		else:
			search = quote(title)
		url = 'https://www.google.de/search?q=%s+-youtube&tbm=isch&source=lnt&tbs=isz:ex,iszw:500,iszh:500' % search
		#print("MDC: Cover: determineContentURL: url: %s" % url)
		return url

	def determineCoverURL(self, result):
		#print("MDC: Cover: determineCoverURL: result: %s" % result)
		urlsraw = re.findall(',"ou":".+?","ow"', result)
		#print("MDC: Cover: determineCoverURL: urlsraw: %s" % urlsraw)
		imageurls = [urlraw[7:-6].encode() for urlraw in urlsraw] # new on 08.02.2017 imageurls=[urlraw[14:-14].encode() for urlraw in urlsraw]
		#print("MDC: Cover: determineCoverURL: imageurls: %s" % imageurls)
		url = imageurls[0] if imageurls else ""
		return url
