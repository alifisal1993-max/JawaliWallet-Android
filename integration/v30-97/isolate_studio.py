from pathlib import Path
import sys
p=Path(sys.argv[1]);s=p.read_text(encoding='utf-8')
assert 'jawali-live.js' in s and 'id="jw-design-panel"' in s and '// V30.87 design studio:' in s
admin=Path(sys.argv[2]);admin.parent.mkdir(parents=True,exist_ok=True)
admin.write_text(s.replace('<script src="jawali-live.js"></script>',''),encoding='utf-8')
a=s.index('<button id="jw-design-open"');b=s.index('<div id="overlay"',a);s=s[:a]+s[b:]
a=s.index('// V30.87 design studio:');b=s.index('</script>',a)
s=s[:a]+'/* Studio isolated in admin-preview. */\n'+s[b:]
a=s.index('function syncDesign(){');b=s.index('// Code 128 Set B:',a)
s=s[:a]+'/* Client uses read-only design defaults. */\napplyDesign();\n'+s[b:]
s=s.replace('</head>','<style>#jw-design-open,#jw-design-panel,#jw-studio{display:none!important;pointer-events:none!important}body.clientApp .jw-register-account{display:none!important}</style></head>',1)
p.write_text(s,encoding='utf-8')
assert 'id="jw-design-open"' not in s and "const shell=document.createElement('div')" not in s
print('Android client customization removed. Admin preview isolated.')
