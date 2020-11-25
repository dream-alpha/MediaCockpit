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


import os
from FileUtils import readFile


def parseFstab():
	mountpoints = []
	lines = readFile("/etc/fstab").splitlines()
	for line in lines:
		if line and not line.startswith("#"):
			line = line.replace("\t", " ")
			words = line.split(" ")
			#print("MDC": MountPointUtils: parseFstab: words: %s" % str(words))
			if len(words) >= 2:
				mountpoint = words[1]
				if mountpoint not in ["none", "/"]:
					mountpoints.append(mountpoint)
	#print("MDC": MountPointUtils: parseFstab: mountpoints: %s" % str(mountpoints))
	return mountpoints


def getMountPointSpaceInfo(path):
	st = os.statvfs(path)
	free = (st.f_bavail * st.f_frsize)
	total = (st.f_blocks * st.f_frsize)
	used = (st.f_blocks - st.f_bfree) * st.f_frsize
	percent_used = round((float(used) / total) * 100, 1) if total > 0 else 0
	return percent_used, used, free


def isMounted(path):
	is_mounted = True
	mountpoint = getMountPoint(path)
	if mountpoint:
		stat = os.stat(mountpoint)
		print("MDC-I: MountPointUtils: isMounted: mountpoint: %s, stat: %s, st_mtime: %s, st_ctime: %s" % (mountpoint, stat, stat.st_mtime, stat.st_ctime))
		is_mounted = not(int(stat.st_mtime) == 0 and int(stat.st_ctime) == 0)
	print("MDC-I: MountPointUtils: isMounted: path: %s, is_mounted: %s" % (path, is_mounted))
	return is_mounted


def getMountPoint(path):
	path = os.path.realpath(path)
	mountpoints = parseFstab()
	mountpoint = None
	for __mountpoint in mountpoints:
		if path.startswith(__mountpoint):
			mountpoint = __mountpoint
			break
	return mountpoint
