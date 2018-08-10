import re
import sys
print('Start...')
for r in range(1,len(sys.argv)):
	file = open(sys.argv[r], 'r+')
	print(sys.argv[r])

	country = re.findall(r'/(?:\w+[-_]?)+\.svg$', sys.argv[r])[0][1:-4]

	content = file.read()
	nodeId = re.findall(r'id="(?:\w+[-_]?)+"[\s>]', content)
	ids = nodeId[:]
	for i in range(len(nodeId)):
		ids[i] = nodeId[i][4:-2]
		print(ids[i])
		content = content.replace('id="' + ids[i] + '"', 'id="' + country + ids[i] + '"')
		variantsOfUse = [['url(#' + ids[i] + ')', 'url(#' + country + ids[i] + ')'],  ['xlinkHref="#' + ids[i] + '"', 'xlinkHref="#' + country + ids[i] + '"']]
		for j in range(len(variantsOfUse)):
			content = content.replace(variantsOfUse[j][0], variantsOfUse[j][1])
	file.seek(0)
	file.write(content)
	file.truncate();
	file.close()
print('Done...')
