import re
import sys
import os
print('Start...')
for r in range(1,len(sys.argv)):
	file = open(sys.argv[r], 'r+')
	print(sys.argv[r])
	content = file.read()
	matches = re.findall(r'svg[^>]*', content)
	country = re.findall(r'/\w{2}\.svg', sys.argv[r])[0][1:-4].upper()
	imports = 'import React from \'react\';\n\rimport pure from \'recompose/pure\';\n\rimport FlagSvgIcon from \'../../FlagSvgIcon\';\n\n\rlet Flag' + country + ' = props => (\n'
	ends = '\r);\nFlag' + country + ' = pure(Flag' + country + ');\nFlag' + country + '.displayName = \'Flag' + country + '\';\nFlag' + country + '.muiName = \'SvgIcon\';\n\nexport default Flag' + country + ';\n\n'
	content = content.replace('\n', '\n    ')
	for i in range(len(matches)):
		content = content.replace(matches[i], 'FlagSvgIcon')
	content = content.replace('<FlagSvgIcon>', '    <FlagSvgIcon {...props}>')
	content = content.replace('</FlagSvgIcon>\n    ', '</FlagSvgIcon>')
	content = imports + content + ends
	file.seek(0)
	file.write(content)
	file.truncate();
	file.close()
	os.rename(sys.argv[r], sys.argv[r].replace('.svg', '.js'))
print('Done...')