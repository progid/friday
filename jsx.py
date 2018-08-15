#!/usr/bin/env python3
"""
Module Docstring
"""

import re
import sys
import os

__author__ = "Igor Terletskiy"
__version__ = "0.1.0"
__license__ = "MIT"

def getJSXFrom(filepath):
	file = open(filepath, 'r+')
	content = file.read()
	print(content, '\n\n\n')

def createJSXDictionary(filelist):
	dictionaryJSX = {}
	for path in filelist:
		dictionaryJSX[path] = getJSXFrom(path)
	return dictionaryJSX

def getListOfFiles(dir, extentions):
	list = []
	for directory in dir:
		for root, dirs, files in os.walk(directory):  
			for filename in files:
				for ext in extentions:
					if re.search(r'.' + ext + '$', filename):
						list.append(root + '/' + filename)
	return list

def main():
	directories = sys.argv[1:] if len(sys.argv) > 1 else ['.']
	extentions = ['js']
	filesList = getListOfFiles(directories, extentions)
	JSXDictionary = createJSXDictionary(filesList)
	


if __name__ == "__main__":
	""" This is executed when run from the command line """
	main()