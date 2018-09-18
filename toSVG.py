import re
import sys
import os

print('Start preparing...')
for r in range(1,len(sys.argv)):
	file = open(sys.argv[r], 'r+')
	content = file.read()
	splitters = ['-', ':']
	for z in range(len(splitters)):
		matchList = re.findall(r'\s\w+(?:' + splitters[z] + '\w+)+\=', content)
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
print('Done preparing...')

print('Start transpiling...')
for r in range(1,len(sys.argv)):
	file = open(sys.argv[r], 'r+')
	print(sys.argv[r])
	content = file.read()
	matches = re.findall(r'svg[^>]*', content)
	country = re.findall(r'/\w+\.svg', sys.argv[r])[0] if re.findall(r'/\w+\.svg', sys.argv[r]) else ''
	print(country)

	imports = 'import React from \'react\';\n\rimport pure from \'recompose/pure\';\n\rimport PaymentTypesSvgIcon from \'../../PaymentTypesSvgIcon\';\n\n\rlet IC' + country + ' = props => (\n'
	ends = '\r);\nIC' + country + ' = pure(IC' + country + ');\nIC' + country + '.displayName = \'IC' + country + '\';\nIC' + country + '.muiName = \'PaymentTypesSvgIcon\';\n\nexport default IC' + country + ';\n\n'
	content = content.replace('\n', '\n    ')
	for i in range(len(matches)):
		content = content.replace(matches[i], 'PaymentTypesSvgIcon')
	content = content.replace('<PaymentTypesSvgIcon>', '    <PaymentTypesSvgIcon {...props}>')
	content = content.replace('</PaymentTypesSvgIcon>\n    ', '</PaymentTypesSvgIcon>')
	content = imports + content + ends
	file.seek(0)
	file.write(content)
	file.truncate();
	file.close()
	os.rename(sys.argv[r], sys.argv[r].replace('.svg', '.js'))
print('Done transpiling...')