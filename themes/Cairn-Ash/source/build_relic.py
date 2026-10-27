from pathlib import Path
import json,base64
root=Path(__file__).resolve().parents[1];theme=root/'obsidian/Cairn Ash'
css=Path(__file__).resolve().with_name('relic-template.css').read_text()
for key,name in [('BASALT_GRAIN','basalt-grain'),('LIMESTONE_GRAIN','limestone-grain'),('BASALT_CHROME','basalt-chrome'),('LIMESTONE_CHROME','limestone-chrome')]:
 css=css.replace(key,'data:image/png;base64,'+base64.b64encode((root/'materials'/(name+'.png')).read_bytes()).decode())
import runpy
css=css.replace('/* LEDGE_TOKENS */',runpy.run_path(str(Path(__file__).resolve().with_name('stone_ledge.py')))['styles'])
(root/'relic.css').write_text(css)
out=root/'obsidian/Cairn Ash Relic';out.mkdir(exist_ok=True)
(out/'theme.css').write_text((theme/'theme.css').read_text()+'\n'+css)
manifest=json.loads((theme/'manifest.json').read_text());manifest['name']='Cairn Ash Relic'
(out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('Built independent Cairn Ash Relic theme and reusable overlay.')
