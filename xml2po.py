#!/usr/bin/python
import sys
import os
from xml.sax import make_parser
from xml.sax.handler import ContentHandler, property_lexical_handler
try:
	from _xmlplus.sax.saxlib import LexicalHandler
	no_comments = False
except ImportError:
	class LexicalHandler():
		def __init__(self):
			pass

	no_comments = True


class parseXML(ContentHandler, LexicalHandler):
	def __init__(self, _attrlist):
		ContentHandler.__init__(self)
		LexicalHandler.__init__(self)
		self.isPointsElement, self.isReboundsElement = 0, 0
		self.last_comment = None

	def comment(self, comment):
		if comment.find("TRANSLATORS:") != -1:
			self.last_comment = comment

	def startElement(self, _name, attrs):
		for x in ["text", "title", "value", "caption"]:
			try:
				attrlist.add((attrs[x], self.last_comment))
				self.last_comment = None
			except KeyError:
				pass


parser = make_parser()
attrlist = set()
contentHandler = parseXML(attrlist)
parser.setContentHandler(contentHandler)
if not no_comments:
	parser.setProperty(property_lexical_handler, contentHandler)

for arg in sys.argv[1:]:
	if os.path.isdir(arg):
		for afile in os.listdir(arg):
			if afile.endswith(".xml"):
				parser.parse(os.path.join(arg, afile))
	else:
		parser.parse(arg)

	attrlist = list(attrlist)
	attrlist.sort(key=lambda a: a[0])

	for (k, c) in attrlist:
		print("")
		print('#: ' + arg)
		k.replace("\\n", "\"\n\"")
		if c:
			for l in c.split('\n'):
				print("#. " + l)
		if k.strip() != "":
			print('msgid "' + k + '"')
			print('msgstr ""')

	attrlist = set()
