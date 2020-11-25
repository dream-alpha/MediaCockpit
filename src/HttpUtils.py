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


import urlparse
from twisted.internet import reactor
from twisted.web.client import HTTPClientFactory


def url_parse(url, defaultPort=None):
	parsed = urlparse.urlparse(url)
	scheme = parsed[0]
	path = urlparse.urlunparse(('', '') + parsed[2:])
	if defaultPort is None:
		if scheme == 'https':
			defaultPort = 443
		else:
			defaultPort = 80
	host, port = parsed[1], defaultPort
	if ':' in host:
		host, port = host.split(':')
		port = int(port)
	return scheme, host, port, path


def sendUrlCommand(url, _contextFactory, timeout, *args, **kwargs):
	_scheme, host, port, _path = url_parse(url)
	factory = MyHTTPClientFactory(url, *args, **kwargs)
	reactor.connectTCP(host, port, factory, timeout=timeout)
	return factory.deferred


class MyHTTPClientFactory(HTTPClientFactory):
	def __init__(self, url, method='GET', postdata=None, headers=None, agent="SHOUTcast", timeout=0, cookies=None, followRedirect=1, _lastModified=None, _etag=None):
		HTTPClientFactory.__init__(
			self, url, method=method, postdata=postdata, headers=headers, agent=agent, timeout=timeout, cookies=cookies,
			followRedirect=followRedirect
		)
