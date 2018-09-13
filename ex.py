import string
import random
import json
import sys

__ids = set()

def randomStringGenerator(size = 10, chars = string.ascii_uppercase + string.ascii_lowercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

def generateAutomationTestLabel():
	str = randomStringGenerator(3)
	x = 0
	while str in __ids:
		print(len(__ids))
		str = randomStringGenerator(13)
	print('\n')
	if str not in __ids:
		__ids.add(str)
	print('__id len: ', len(__ids))


def main():
	for i in range(0, 238328):
		generateAutomationTestLabel()
	file = open('xxx.txt', 'w+')
	file.seek(0)
	file.write(json.dumps(list(__ids)))
	file.truncate()
	file.close()

if __name__ == "__main__":
	""" This is executed when run from the command line """
	main()