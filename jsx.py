#!/usr/bin/env python3
"""
Module Docstring
"""

import re
import sys
import os

__author__ = "Igor Terletskiy"
__version__ = "0.1.1"
__license__ = "MIT"

def addSymbols(start, end):
	temp = set()
	for i in range(ord(start), ord(end)+1):
		temp.add(chr(i))
	return temp

symbols = {
	'startTag': {'<'},
	'endTag': {'/', '>'},
	'iteruptions': {'\n', ' ', '\t', '\r', '\b'},
	'stringLiterals': {'\'', '"', '`'},
	'startExpressionLiteral': {'{'},
	'endExpressionLiteral': {'}'}
	'assign': {'='}
	'alphabet': addSymbols('0', '9')
	 | addSymbols('a', 'z')
	 | addSymbols('A', 'Z')
	 | addSymbols('а', 'я')
	 | addSymbols('А', 'Я')
	 | {'-', '_', 'ё', 'Ё', 'є', 'Є', 'і', 'І', 'ї', 'Ї', 'ґ', 'Ґ'}
}

def getJSXFrom(filepath):
	file = open(filepath, 'r+')
	content = file.read()
	# print('\n' + filepath + '\n')
	tempStr = ''
	writable = False
	closingTagRequest = False
	result = []
	for i in range(len(content)):
		s = content[i]
		t = symbols
		if s in t.startTag and not writable:
			writable = True
		if s in t.endTag and writable:
			if closingTagRequest:
				if s in t.iteruptions
			if s == '/' and not closingTagRequest:
				closingTagRequest = True
			writable = False
		if writable:
			tempStr += s


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