import re
import sys
import os
print('Start...')
for r in range(1,len(sys.argv)):
	file = open(sys.argv[r], 'r+')
	print(sys.argv[r])
	content = file.read()
	matches = re.findall(r'svg[^>]*', content)
	country = re.findall(r'/\w+\.svg', sys.argv[r])[0] if re.findall(r'/\w+\.svg', sys.argv[r]) else ''
	print(country)

	imports = 'import React from \'react\';\n\rimport pure from \'recompose/pure\';\n\rimport SvgIcon from \'@liqpay/material-ui/SvgIcon\';\n\n\rlet IC' + country + ' = props => (\n'
	ends = '\r);\nIC' + country + ' = pure(IC' + country + ');\nIC' + country + '.displayName = \'IC' + country + '\';\nIC' + country + '.muiName = \'SvgIcon\';\n\nexport default IC' + country + ';\n\n'
	content = content.replace('\n', '\n    ')
	for i in range(len(matches)):
		content = content.replace(matches[i], 'SvgIcon')
	content = content.replace('<SvgIcon>', '    <SvgIcon {...props}>')
	content = content.replace('</SvgIcon>\n    ', '</SvgIcon>')
	content = imports + content + ends
	file.seek(0)
	file.write(content)
	file.truncate();
	file.close()
	os.rename(sys.argv[r], sys.argv[r].replace('.svg', '.js'))
print('Done...')