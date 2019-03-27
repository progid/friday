import re
import sys
print('Start...')
for r in range(1,len(sys.argv)):
	file = open(sys.argv[r], 'r+')
	content = file.read()
	splitters = ['-', ':']
	for z in range(len(splitters)):
		matchList = re.findall(r'\s\w+(?:' + splitters[z] + r'\w+)+\=', content)
		preparedMatchList = [];
		for i in range(len(matchList)):
			temp = matchList[i].split(splitters[z])
			preparedMatchList.append([]);
			for j in temp:
				preparedMatchList[i].append(j.capitalize())
			preparedMatchList[i] = ''.join(preparedMatchList[i])
			content = content.replace(matchList[i], preparedMatchList[i])
	file.seek(0)
	file.write(content)
	file.truncate();
	file.close()
print('Done...')
