import string
import random
import json
import sys
import math

def addSymbols(start, end):
	temp = set()
	for i in range(ord(start), ord(end)+1):
		temp.add(chr(i))
	return temp

__ids = set()
__nodesCount = 2
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

def randomStringGenerator(size = 10, chars = __idAlphabet):
    return ''.join(random.choice(chars) for _ in range(size))

def generateAutomationTestLabel():
	length = math.ceil(math.log(__nodesCount, len(__idAlphabet)))
	length = length if length else 3
	str = randomStringGenerator(length)
	while str in __ids:
		str = randomStringGenerator(length)
	if str not in __ids:
		__ids.add(str)
	return str


element1 = {
	'tagName': 'TestTag',
	'props': {
		'action': 'x',
		'icon': '<IconDefault>'
	}
}
element2 = {
	'tagName': 'TestTag',
	'props': {
		'action': 'x',
		'icon': '<IconDefault>',
		'key': '{item.key}'
	}
}

def addTestableLabelFor(element):
	if 'props' not in element:
		element['props'] = dict()
	if 'id' not in element['props'] or element['props']['id'] == '':
		element['props']['testable'] = '\'' + generateAutomationTestLabel() + '\''
		if 'key' in element['props']:
			if element['props']['key'][0:1] in __symbols['startExpressionLiteral']:
				element['props']['testable'] = '{' + element['props']['testable'] + ' + ' + element['props']['key'][1:-1] + '}' 
			elif  element['props']['key'][0:1] in __symbols['stringLiterals']:
				element['props']['testable'] = element['props']['testable'] + element['props']['key']
	return element

def main():
	print(addTestableLabelFor(element2))
	

if __name__ == "__main__":
	""" This is executed when run from the command line """
	main()