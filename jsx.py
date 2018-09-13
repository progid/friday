#!/usr/bin/env python3
"""
Module Docstring
"""

import re
import sys
import os
import json
import copy
import zlib
import string
import random

__author__ = "Igor Terletskiy"
__version__ = "0.2.1"
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
	 | {'-', '_', '/', '{', 'ё', 'Ё', 'є', 'Є', 'і', 'І', 'ї', 'Ї', 'ґ', 'Ґ'}
}

__ids = set()
__nodesCount = 0

def randomStringGenerator(size = 10, chars = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def generateAutomationTestLabel():
	str = randomStringGenerator(30)
	if str in __ids:
		generateAutomationTestLabel()
	else:
		__ids.append(str)

def dependencyAnalyzer(oldJSXDictionary, JSXDictionary):
	# print(oldJSXDictionary, JSXDictionary)
	print('')

def clearDictionaryForUnusedAttr(dictionary):
	result = {}
	for key in dictionary:
		items = copy.deepcopy(dictionary[key])
		result[key] = removeUnusedAttr(items)
	global __nodesCount
	print(__nodesCount)
	return result

def removeUnusedAttr(itemArr):
	global __nodesCount
	for i in range(len(itemArr)):
		__nodesCount = __nodesCount + 1
		element = itemArr[i]
		if 'closed' in element:
			del element['closed']
		if 'props' in element and not len(element['props']):
			del element['props']
		if 'children' in element and not len(element['children']):
			del element['children']
		elif 'children' in element and len(element['children']):
			removeUnusedAttr(element['children'])
	return itemArr

def clearArray(array):
	if '' in array:
		array.remove('')
		return clearArray(array)
	return array

def buildDictFromArray(array, generatedDict={}):
	if '=' in array:
		pos = array.index('=')
		generatedDict[array[pos - 1]] = array[pos + 1]
		array[pos-1] = ''
		array[pos] = ''
		array[pos + 1] = ''
		return buildDictFromArray(array, generatedDict)
	clearArray(array)
	return generatedDict

def makeNested(mapArray, completeArray, closeTagName):
	if not len(mapArray):
		return completeArray
	element = mapArray.pop(0)
	if element['closed']:
		completeArray.append(element)
	else:
		if element['tagName'][0:1] == '/' and element['tagName'][1:] == closeTagName:
			return completeArray;
		else:
			completeArray.append(element)
			makeNested(mapArray, element['children'], element['tagName'])
	return makeNested(mapArray, completeArray, closeTagName)

def prepareJSXDictionary(dictionary):
	result = {}
	for key in dictionary:
		if len(dictionary[key]):
			result[key] = dictionary[key]
	for key in result:
		currentItem = result[key]
		temp = []
		for i in range(len(currentItem)):
			props = dict(buildDictFromArray(currentItem[i], {}))
			closed = False
			for j in range(1, len(currentItem[i])):
				if currentItem[i][0] != '/':
					if currentItem[i][j] == '/':
						closed = True
					else:
						props[currentItem[i][j]] = True
					currentItem[i][j] = ''
			item = {
				'tagName': currentItem[i][0] if currentItem[i][0] != '/' else ''.join(currentItem[i]),
				'props': props,
				'closed': closed
			}
			if not closed:
				item['children'] = []
			temp.append(item)
		result[key] = temp
	for key in result:
		result[key] = makeNested(copy.deepcopy(result[key]), [],  '')
	return result;

def getJSXFrom(filepath):
	file = open(filepath, 'r+')
	content = file.read()
	result = findJSX(content)
	return result

def findJSX(content):
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
				if s == '{':
					isItExpression = True
					isItPropsValue = True
					propsStartSymbol = s
					propsEndSymbol = '}'
					propsDeep += 1
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
			tempStr = ''
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

def logJsonToFile(JsonData, filepath = 'out.txt'):
	file = open(filepath, 'w+')
	file.seek(0)
	file.write(json.dumps(JsonData))
	file.truncate();
	file.close()

def saveToFile(JsonData, filepath = 'saved.testablerc'):
	file = open(filepath, 'wb')
	file.seek(0)
	file.write(zlib.compress(json.dumps(JsonData).encode("utf-8")))
	file.truncate();
	file.close()

def loadFromFile(filepath = 'saved.testablerc'):
	file = open(filepath, 'rb')
	content = file.read()
	uncompress = zlib.decompress(content)
	return json.loads(uncompress)

def main():
	directories = sys.argv[1:] if len(sys.argv) > 1 else ['.']
	extentions = ['js']
	filesList = getListOfFiles(directories, extentions)
	rawJSXDictionary = createJSXDictionary(filesList)
	completeJSXDictionary = prepareJSXDictionary(rawJSXDictionary)
	minimisedJSXDictionary = clearDictionaryForUnusedAttr(completeJSXDictionary)
	dependencyAnalyzer(loadFromFile(), minimisedJSXDictionary)
	# logJsonToFile()
	# saveToFile(minimisedJSXDictionary)
	# loadFromFile()


if __name__ == "__main__":
	""" This is executed when run from the command line """
	main()