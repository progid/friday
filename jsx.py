#!/usr/bin/env python3
"""
Module Docstring
"""

import re
import sys
import os
import json

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
	'common': {'\\'},
	'endTag': {'/', '>'},
	'iteruptions': {'\n', ' ', '\t', '\r', '\b'},
	'stringLiterals': {'\'', '"', '`'},
	'startExpressionLiteral': {'{'},
	'endExpressionLiteral': {'}'},
	'assign': {'='},
	'alphabet': addSymbols('0', '9')
	 | addSymbols('a', 'z')
	 | addSymbols('A', 'Z')
	 | addSymbols('а', 'я')
	 | addSymbols('А', 'Я')
	 | {'-', '_', 'ё', 'Ё', 'є', 'Є', 'і', 'І', 'ї', 'Ї', 'ґ', 'Ґ'}
}

print(symbols['alphabet'])

def getJSXFrom(filepath):
	file = open(filepath, 'r+')
	content = file.read()
	result = findJSX(content)
	return result

def findJSX(content):
	# print('\n' + filepath + '\n')
	tempStr = ''
	writable = False
	closingTagRequest = False
	tag = []
	result = []
	propsDeep = 0
	propsStartSymbol = ''
	propsEndSymbol = ''
	isItExpression = False
	isItString = False
	isItPropsValue = False
	stringScreening = False
	for i in range(len(content)):

		s = content[i]
		t = symbols

		if writable:
			if stringScreening:
				tempStr += s
				stringScreening = False
				continue
			if closingTagRequest and s != '>':
				writable = False
				closingTagRequest = False
				tempStr = ''
				tag = []
				continue
			if isItPropsValue:
				if isItString:
					if s in t['common']:
						stringScreening = True
					elif s == propsEndSymbol:
						isItString = False
						isItPropsValue = False
					tempStr += s
				elif isItExpression:
					if s in t['common']:
						stringScreening = True
					elif s == propsStartSymbol:
						propsDeep += 1
					elif s == propsEndSymbol:
						propsDeep -= 1
					if propsDeep == 0:
						isItExpression = False
						isItPropsValue = False
					tempStr += s
				else:
					if s in t['stringLiterals']:
						propsStartSymbol = s
						propsEndSymbol = s
						isItString = True
						tempStr += s
					if s in t['startExpressionLiteral']:
						isItExpression = True
						propsStartSymbol = s
						propsEndSymbol = '}'
						propsDeep += 1
						tempStr += s
				continue

			if s in t['iteruptions']:
				if len(tempStr) > 0:
					tag.append(tempStr)
					tempStr = ''
				continue
			if s in t['alphabet']:
				tempStr += s
				continue
			elif s in t['assign']:
				isItPropsValue = True
				tag.append(tempStr)
				tag.append('=')
				tempStr = ''
				continue

			if s in t['endTag']:
				if s == '>':
					tag.append(tempStr)
					result.append(tag)
					tag = []
					writable = False
					closingTagRequest = False
					tempStr = ''
					continue
				if s == '/' and not closingTagRequest:
					closingTagRequest = True
					continue
			tag = []
			writable = False
		elif s in t['startTag']:
			writable = True
	return result

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

	file = open('out.txt', 'w+')
	file.seek(0)
	file.write(json.dumps(JSXDictionary))
	file.truncate();
	file.close()


if __name__ == "__main__":
	""" This is executed when run from the command line """
	main()