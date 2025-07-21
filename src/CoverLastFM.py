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


import json
from six.moves.urllib.parse import quote
from .Debug import logger
from .Cover import Cover


class CoverLastFM(Cover):
    def __init__(self, download_dir, coverDownloadFinished, coverDownloadFailed):
        self.LASTFM_API_KEY = "ef17c11a7ab9835c10983acad60a123c"
        self.LASTFM_URL = "http://ws.audioscrobbler.com/2.0/"
        Cover.__init__(self, download_dir,
                       coverDownloadFinished, coverDownloadFailed)

    def determineContentURL(self, artist, album, title):
        logger.info("artist: %s, album: %s, title: %s", artist, album, title)
        self.artist = artist.encode('utf8')
        self.album = album.encode('utf8')
        url = self.LASTFM_URL\
            + "?method=album.search"\
            + "&api_key=" + self.LASTFM_API_KEY\
            + "&album=" + quote(album)\
            + "&format=json"
        logger.debug("url: %s", url)
        return url

    def determineCoverURL(self, result):

        def getImageUrl(album):
            logger.debug("### album: %s", album)
            url = ""
            for image in album["image"]:
                logger.debug("     %s, %s", image["#text"], image["size"])
                for resolution in ["extralarge", "large"]:
                    logger.debug("     - %s", resolution)
                    if image["size"] == resolution:
                        url = str(image["#text"])
                        break
                if url:
                    break
            return url

        logger.debug("artist: %s", self.artist)
        url = ""
        root = json.loads(result)
        if "results" in root:
            logger.debug(
                "### album and artist ###############################")
            for album in root["results"]["albummatches"]["album"]:
                logger.debug("     >>> %s, %s", album["name"], album["artist"])
                if self.artist.lower() in album["artist"].lower():
                    url = getImageUrl(album)
                    if url:
                        break
            if not url:
                logger.debug(
                    "### album only ######################################")
                for album in root["results"]["albummatches"]["album"]:
                    url = getImageUrl(album)
                    if url:
                        break
        elif "message" in root:
            logger.error("%s", root["message"])
        logger.debug("url: %s", url)
        return url
