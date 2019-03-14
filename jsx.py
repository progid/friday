#!/usr/bin/env python3
"""
Module Docstring
"""

import re, sys, os, json, copy, zlib, string, random, math

__author__ = "Igor Terletskiy"
__version__ = "0.2.2"
__license__ = "MIT"

__ids = set()
__nodesCount = 0
__idLength = 3
__idAlphabet = string.ascii_letters + string.digits
__config = dict()

def loadConfigFile(filepath):
	global __config
	confFile = open(filepath)
	__config['blacklist'] = set()
	


def addSymbols(start, end):
	temp = set()
	for i in range(ord(start), ord(end)+1):
		temp.add(chr(i))
	return temp

__symbols = {
	'startTag': {'<'},
	'common': {'\\'},
	'endTag': {'/', '>'},
	'iteruptions': {'\n', ' ', '\t', '\r', '\b'},
	'stringLiterals': {'\'', '"', '`'},
	'startExpressionLiteral': {'{'},
	'endExpressionLiteral': {'}'},
	'assign': {'='},
	'alphabet': addSymbols('а', 'я')
	 | addSymbols('А', 'Я')
	 | set('-_/{ёЁєЄіІїЇґҐ' + __idAlphabet)
}

def randomStringGenerator(size = 10, chars = __idAlphabet):
    return ''.join(random.choice(chars) for _ in range(size))

def generateAutomationTestLabel():
	global __idLength
	__idLength = math.ceil(math.log(__nodesCount, len(__idAlphabet)))
	__idLength = __idLength if __idLength else 3
	str = randomStringGenerator(__idLength)
	while str in __ids:
		str = randomStringGenerator(__idLength)
	if str not in __ids:
		__ids.add(str)
	return str

def makeListFromDict(JSXDict):
	result = dict()
	for key in JSXDict:
		result[key] = recfuncMakeListFromDict(copy.deepcopy(JSXDict[key]))
	return result

def recfuncMakeListFromDict(elements):
	result = []
	for i in range(len(elements)):
		item = elements[i]
		result.append([
			item['tagName'],
			item['props']['testable'],
			item['closed'],
			item['length']
		])
		if 'children' in item:
			result = result + recfuncMakeListFromDict(item['children'])
		if not item['closed']:
			result.append(['/' + item['tagName']])

	return result

def addTestableToDOM(JSXModel):
	global __idLength, __symbols
	tagWord = r'__' + randomStringGenerator(2 ** __idLength) + r'__'
	tagWordLength = len(tagWord) + 2
	testableLength = 17 + __idLength
	print(tagWord)
	for key in JSXModel:
		file = open(key, 'r+')
		content = file.read()
		items = JSXModel[key]
		iteruptions = re.sub(r'[\'\"{}\,\s]', '', str(__symbols['iteruptions'])) + r'\s'
		offset = 0
		for i in range(len(items)):
			item = items[i]
			pattern = r''
			
			if item[0][0] == '/':
				pattern = r'<[' + iteruptions + r']*\/[' + iteruptions + r']*' + item[0][1:] + r'[' + iteruptions + r']*>'
				found = re.search(pattern, content[offset:])
				if not found:
					print(item, key)
				offset = offset + found.span()[1]
				content = content[:offset] + '</' + tagWord + '>' + content[offset:]
				offset = offset + tagWordLength + 1
			else:
				pattern = r'<[' + iteruptions + r']*' + item[0]
				found = re.search(pattern, content[offset:])
				offset = offset + found.span()[0]
				if not item[2]:
					content = content[:offset] + '<' + tagWord + ' data-testable=' + item[1] + '>' + content[offset:]
					print('offset + tagWordLength + testableLength', offset, tagWordLength, testableLength)
					offset = offset + tagWordLength + testableLength + item[3]
					print('after', offset)
				else:
					content = content[:offset] + '<' + tagWord + ' data-testable=' + item[1] + '>' + content[offset:offset + item[3]] + '</' + tagWord + '>' + content[offset + item[3]:]
					print('before simple', offset)
					offset = offset + item[3] + tagWordLength * 2 + 1 + testableLength
					print('after simple', offset)
		content = content.replace(r'<' + tagWord + r' data-testable=', '<div data-testable=')
		content = content.replace(r'</' + tagWord + r'>', '</div>')
		file.seek(0)
		file.write(content)
		file.truncate()
		file.close()

def dependencyAnalyzer(oldJSXDictionary, JSXDictionary):
	for i in range(__nodesCount):
		generateAutomationTestLabel()
	print(__ids)

def clearDictionaryForUnusedAttr(dictionary):
	result = {}
	global __nodesCount
	__nodesCount = 0
	for key in dictionary:
		items = copy.deepcopy(dictionary[key])
		result[key] = removeUnusedAttr(items)
	return result

def addTestableLabelFor(element):
	if 'props' not in element:
		element['props'] = dict()
	if 'id' not in element['props'] or element['props']['id'] == '':
		element['props']['testable'] = '\'' + generateAutomationTestLabel() + '\''
		if 'key' in element['props']:
			if element['props']['key'][0:1] in __symbols['startExpressionLiteral']:
				element['props']['testable'] = '{' + element['props']['testable'] + ' + (' +  element['props']['key'][1:-1] + ')}' 
			elif  element['props']['key'][0:1] in __symbols['stringLiterals']:
				element['props']['testable'] = '{' + element['props']['testable'] + ' + ' +  element['props']['key'] + '}'
	else:
		element['props']['testable'] = element['props']['id']
	return element

def removeUnusedAttr(itemArr):
	global __nodesCount
	for i in range(len(itemArr)):
		__nodesCount = __nodesCount + 1
		element = itemArr[i]

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

def recursivelyAddTestableForJSXDict(items):
	for i in range(len(items)):
		item = items[i]
		addTestableLabelFor(item)
		if 'children' in item:
			recursivelyAddTestableForJSXDict(item['children'])
	return items

def firstSetOfTestableLabels(JSXDict):
	result = dict()
	for key in JSXDict:
		result[key] = recursivelyAddTestableForJSXDict(copy.deepcopy(JSXDict[key]))
	return result

def buildDictFromArray(array, generatedDict={}):
	if '=' in array:
		pos = array.index('=')
		generatedDict[array[pos - 1]] = array[pos + 1]
		array[pos-1] = array[pos] = array[pos + 1] = ''
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
			return completeArray
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
			length = -1

			if 'length' in props:
				length = props['length']
				del props['length']

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
			item['length'] = length
			temp.append(item)
		result[key] = temp
	for key in result:
		result[key] = makeNested(copy.deepcopy(result[key]), [],  '')
	return result

def getJSXFrom(filepath):
	file = open(filepath, 'r+')
	content = file.read()
	result = findJSX(content)
	return result

def findJSX(content):
	global __symbols
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
	length = 0
	for i in range(len(content)):

		s = content[i]
		t = __symbols

		if writable:
			length = length + 1
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
					tag = tag + ['length', '=', length]
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
			length = 1
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
	file.truncate()
	file.close()

def saveToFile(JsonData, filepath = 'saved.testablerc'):
	file = open(filepath, 'wb')
	file.seek(0)
	file.write(zlib.compress(json.dumps(JsonData).encode("utf-8")))
	file.truncate()
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
	withTestableLabels = firstSetOfTestableLabels(minimisedJSXDictionary)
	listJSX = makeListFromDict(withTestableLabels)
	addTestableToDOM(listJSX)
	#dependencyAnalyzer(loadFromFile(), minimisedJSXDictionary)
	logJsonToFile(listJSX)
	# saveToFile(minimisedJSXDictionary)
	# loadFromFile()


if __name__ == "__main__":
	""" This is executed when run from the command line """
	main()