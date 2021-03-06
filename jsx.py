#!/usr/bin/env python3
"""
Module Docstring
"""
import re, sys, os, json, copy, zlib, string, random, math, hashlib

__author__ = "Igor Terletskiy"
__version__ = "0.3.2"
__license__ = "MIT"

def addSymbols(start, end):
	temp = set()
	for i in range(ord(start), ord(end)+1):
		temp.add(chr(i))
	return temp

__ids = set()
__nodesCount = 0
__idAlphabet = string.ascii_letters + string.digits
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
__whitelist = { 'br', 'b', 'i', 's', 'm' }

def randomStringGenerator(size = 10, chars = __idAlphabet):
    return ''.join(random.choice(chars) for _ in range(size))

def generateAutomationTestLabel(label = ''):
	length = max(math.ceil(math.log(__nodesCount, len(__idAlphabet))), 3)
	str = label if label else randomStringGenerator(length)
	while str in __ids:
		str = randomStringGenerator(length)
	if str not in __ids:
		__ids.add(str)
	return str

def makeListFromDict(JSXDict, callback):
	result = dict()
	for key in JSXDict:
		result[key] = callback(copy.deepcopy(JSXDict[key]))
	return result

def recfuncMakeListFromDict(elements):
	result = []
	for i in range(len(elements)):
		item = elements[i]
		result.append([item['tagName'], item['props']['testable'], 'children' not in item])
		if 'children' in item:
			result = result + recfuncMakeListFromDict(item['children'])
			result.append(['/' + item['tagName']])
	return result

def recfuncMakeListFromDictWithoutLabels(elements):
	result = []
	for i in range(len(elements)):
		item = elements[i]
		result.append([
			item['tagName'],
			hashlib.md5(json.dumps(item['props'], ensure_ascii=False).encode('utf8')).hexdigest() if 'props' in item else '',
			False if 'children' not in item else hashlib.md5(json.dumps(item['children'], ensure_ascii=False).encode('utf8')).hexdigest()
		])
		if 'children' in item:
			result = result + recfuncMakeListFromDictWithoutLabels(item['children'])
			result.append(['/' + item['tagName']])
	return result

def addTestableToDOM(JSXModel):
	for key in JSXModel:
		file = open(key, 'r+')
		content = file.read()
		items = JSXModel[key]
		for i in range(len(items)):
			item = items[i]
			print(item)
			if(item[0][0] != '/'):
				pattern = r'<' + item[0] + r'\s(?!data-testable)'
				content = re.sub(pattern, '<' + item[0] + ' data-testable=' + item[1] + ' ', content, 1)
		file.seek(0)
		file.write(content)
		file.truncate()
		file.close()

def dependencyAnalyzer(oldJSXDictionary, JSXDictionary):
	print(oldJSXDictionary, JSXDictionary)
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
		array[pos-1] = ''
		array[pos] = ''
		array[pos + 1] = ''
		return buildDictFromArray(array, generatedDict)
	clearArray(array)
	return generatedDict

def dictToHash(dictionary):
	dict = copy.deepcopy(dictionary)
	for key in dict:
		dict[key] = hashlib.md5(json.dumps(dict[key], ensure_ascii=False).encode('utf8')).hexdigest()
	return dict

def getChangedListOfFiles(newDict, oldDict):
	newHashesDict = dictToHash(newDict)
	oldHashesDict = dictToHash(oldDict)
	result = copy.deepcopy(newDict)
	for key in newHashesDict:
		if key in oldHashesDict and oldHashesDict[key] == newHashesDict[key]:
			del result[key]
	return list(result.keys())

def getChangedFiles(newDict, oldDict):
	filesList = getChangedListOfFiles(newDict, oldDict)
	result = {'current': {}, 'previous': {}}
	for key in filesList:
		result['current'][key] = copy.deepcopy(newDict[key])
		result['previous'][key] = copy.deepcopy(oldDict[key]) if key in oldDict else {}
	result['current'] = makeListFromDict(result['current'], recfuncMakeListFromDictWithoutLabels)
	result['previous'] = makeListFromDict(result['previous'], recfuncMakeListFromDictWithoutLabels)
	return result

def removeDuplicatesOfComparsionModel(model):
	newModel = model['current']
	oldModel = model['previous']
	modelKeys = list(newModel.keys())
	tag = False
	tagWeight = 0

	for key in modelKeys:
		for i in range(len(newModel[key])):
			item = newModel[key][i]
			if tag:
				if '/' + tag == item[0]:
					tagWeight -= 1
					if tagWeight == 0:
						tag = False
				elif item[0] == tag and len(item) >= 3 and item[2]:
					tagWeight += 1
				newModel[key][i] = ''
			else:
				for j in range(len(oldModel[key])):
					subitem = oldModel[key][j]
					if not tag:
						if len(item) >= 2 and len(subitem) >= 2 and item[1] == subitem[1] and item[0] == subitem[0]:
							if len(item) >= 3 and len(subitem) >= 3 and item[2] == subitem[2] and item[2]:
								tag = subitem[0]
								tagWeight = 1
								oldModel[key][j] = ''
								newModel[key][i] = ''
							elif len(item) >= 3 and len(subitem) >= 3 and not item[2]:
								oldModel[key][j] = ''
								newModel[key][i] = ''
								break
					else:
						if len(subitem) >= 1 and '/' + tag == subitem[0]:
							tagWeight -= 1
							if tagWeight == 0:
								oldModel[key][j] = ''
								tagWeight = 1
								break
						elif len(subitem) >= 3 and subitem[0] == tag and subitem[2]:
							tagWeight += 1
						oldModel[key][j] = ''
		clearArray(newModel[key])
		clearArray(oldModel[key])
	return model

def addLabelsForNewTags(model):
	newModel = model['current']
	oldModel = model['previous']
	modelKeys = list(model['current'].keys())
	exceptionKeys = []
	for key in modelKeys:
		if not len(oldModel[key]):
			for i in range(len(newModel[key])):
				newModel[key][i].append('new')
			exceptionKeys.append(key)
	modelKeys = list(set(modelKeys) - set(exceptionKeys))
	for key in modelKeys:
		for i in range(len(newModel[key])):
			item = newModel[key][i]
			for j in range(len(oldModel[key])):
				subitem = oldModel[key][j]
				if item[0] == subitem[0]:
					if item[1] == subitem[1]:
						
				elif item[1] == subitem[1]:
					# <-------------------------------------------------------------------------------------------------------------
				else:
					# <-------------------------------------------------------------------------------------------------------------

				
	return model

def handleChangedBlocksOfComparsionModel(model):
	pureModel = removeDuplicatesOfComparsionModel(model)
	withLabelsForNewTags = addLabelsForNewTags(pureModel)
	return withLabelsForNewTags

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
	for i in range(len(content)):

		s = content[i]
		t = __symbols

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

def toFile(data, filepath, mode):
	file = open(filepath, mode)
	file.seek(0)
	file.write(data)
	file.truncate()
	file.close()

def logJsonToFile(data, filepath = 'out.txt'):
	toFile(json.dumps(data), filepath, 'w+')

def saveToFile(JsonData, filepath = 'saved.testablerc'):
	toFile(zlib.compress(json.dumps(JsonData).encode("utf-8")), filepath, 'wb')

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
	listJSX = makeListFromDict(withTestableLabels, recfuncMakeListFromDict)
	oldJSXDictionary = loadFromFile()
	# changedFilesList = getListOfChangedFiles(minimisedJSXDictionary, oldJSXDictionary)
	# oldVersionChangedFiles
	# getChangedBlocksOfFiles(changedFiles, oldJSXDictionary)
	# logJsonToFile(getChangedFiles(minimisedJSXDictionary, oldJSXDictionary))
	comparsionModel = getChangedFiles(minimisedJSXDictionary, oldJSXDictionary)
	logJsonToFile(handleChangedBlocksOfComparsionModel(comparsionModel))
	# logJsonToFile(comparsionModel)
	# dependencyAnalyzer(loadFromFile(), minimisedJSXDictionary)
	# addTestableToDOM(listJSX)
	# saveToFile(minimisedJSXDictionary)
	generateAutomationTestLabel()

if __name__ == "__main__":
	""" This is executed when run from the command line """
	main()