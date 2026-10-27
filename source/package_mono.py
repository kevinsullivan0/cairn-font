from pathlib import Path
import base64,html,json
import argparse
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent.parent)
root=p.parse_args().output
styles=[('Regular',400,'normal'),('Italic',400,'italic'),('Bold',700,'normal'),('BoldItalic',700,'italic')]
for embedded in [False,True]:
 faces=[]
 for key,weight,style in styles:
  url='data:font/woff;base64,'+base64.b64encode((root/'web/fonts'/f'CairnMono-{key}.woff').read_bytes()).decode() if embedded else f'fonts/CairnMono-{key}.woff'
  faces.append(f'@font-face {{font-family:"Cairn Mono";src:url("{url}") format("woff");font-weight:{weight};font-style:{style};font-display:swap;}}')
 faces.append(':root {--font-cairn-mono:"Cairn Mono","JetBrainsMono Nerd Font",ui-monospace,monospace;}\n.cairn-code {font-family:var(--font-cairn-mono);font-kerning:none;font-variant-ligatures:none;font-synthesis:none;tab-size:4;}')
 (root/'web'/('cairn-mono-embedded.css' if embedded else 'cairn-mono.css')).write_text('\n'.join(faces)+'\n')
css=(root/'web/cairn-mono-embedded.css').read_text()
sample='''# A record of the last watch
from pathlib import Path

def remember(names: list[str]) -> int:
    for index, name in enumerate(names):
        if name != "0" and len(name) >= 1:
            print(f"{index:02d}: {name}")
    return len(names)

count = remember(["Keeper", "Mason"])
assert count == 2

# Distinguish symbols and follow columns:
# Il1|!  O0Q  rn m  [] {} ()  <> /\\
# != == <= >= => ->  +-*/%  &|^~  :;.,
# 0123456789  `quoted`  "double"  'single'
# name       | count | state
# keeper     |    12 | awake
# mason      |     3 | ready
'''
page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cairn Mono / Code study</title><style>FONT_CSS
*{box-sizing:border-box}body{margin:0;background:#1b1615;color:#e3d4ba;font:15px/1.6 system-ui}main{max-width:1200px;margin:auto;padding:35px 25px}h1{font-size:36px;font-weight:500;color:#d3ad73;margin-bottom:10px}a{color:#d3ad73}.tools{display:flex;flex-wrap:wrap;gap:20px;padding:20px 0}textarea{width:100%;min-height:670px;background:#251e1a;color:#e3d4ba;border:1px solid #574437;padding:25px;resize:vertical;white-space:pre;overflow:auto;font-size:18px;line-height:1.65}select{font:inherit;background:#251e1a;color:#e3d4ba;padding:6px}input,select,textarea{accent-color:#d3ad73}.note{color:#af9b84;max-width:850px}button{font:inherit;padding:6px 12px;background:#d3ad73;color:#1b1615;border:0;border-radius:3px}.proof{width:100%;margin-top:35px}body.light{background:#f1e6cf;color:#392c24}body.light h1,body.light a{color:#855021}body.light .note{color:#705b47}body.light textarea,body.light select{background:#e8d9bd;color:#392c24;border-color:#ab9170}:focus-visible{outline:2px solid #d3ad73;outline-offset:3px}</style><main><h1>Cairn Mono</h1><p class="note">The same carved voice, in equal-width cells. Compact wide letters, clearer i/l/1, a slashed zero, and room for punctuation. All four real styles are embedded.</p><div class="tools"><label>Size <input id="size" type="range" min="12" max="28" value="18"><output id="size-label">18 px</output></label><label>Style <select id="style"><option value="Regular">Regular</option><option value="Italic">Italic</option><option value="Bold">Bold</option><option value="BoldItalic">Bold Italic</option></select></label><button id="theme" aria-pressed="false">Light background</button></div><label for="code">Edit this code to try the font</label><textarea spellcheck="false" id="code" class="cairn-code">SAMPLE</textarea><p class="note" id="coverage"></p><p class="note">Start at 18 px. Every supported glyph advances 0.75 em, with no kerning or code ligatures. The character set matches Cairn: printable ASCII and selected punctuation/symbols; Nerd Font icons and accented letters use fallback fonts. It is a first monospace edition, without manual hinting.</p><p><a href="specimen.html">Proportional Cairn</a> · <a href="../Cairn-Dragnipur/preview.html">Try the Dragnipur palettes</a> · <a href="README.html">Package guide</a></p><img class="proof" src="proofs/mono.png" alt="Cairn Mono rendered at several sizes in four styles"></main><script>
const $=id=>document.getElementById(id);const supported=new Set(COVERAGE);
$('size').oninput=()=>{$('code').style.fontSize=$('size').value+'px';$('size-label').textContent=$('size').value+' px';};
$('style').onchange=()=>{const v=$('style').value;$('code').style.fontWeight=v.includes('Bold')?'700':'400';$('code').style.fontStyle=v.includes('Italic')?'italic':'normal';};
$('theme').onclick=()=>{const light=document.body.classList.toggle('light');$('theme').setAttribute('aria-pressed',String(light));$('theme').textContent=light?'Dark background':'Light background';};
function coverage(){const missing=[...new Set([...$('code').value].filter(c=>!supported.has(c.codePointAt(0))&&!['\\n','\\t','\\r'].includes(c)))];$('coverage').textContent=missing.length?'Fallback characters in this sample: '+missing.join(' '):'Every character in this sample is drawn in Cairn Mono.';}
$('code').oninput=coverage;coverage();
</script></html>'''
from fontTools.ttLib import TTFont
page=page.replace('FONT_CSS',css).replace('SAMPLE',html.escape(sample)).replace('COVERAGE',json.dumps(sorted(TTFont(root/'desktop/CairnMono-Regular.ttf').getBestCmap())))
# Keep the standalone font archive independent of the separate local theme package.
page=page.replace('<a href="../Cairn-Dragnipur/preview.html">Try the Dragnipur palettes</a> · ','')
(root/'mono-specimen.html').write_text(page)
p=root/'specimen.html';s=p.read_text();s=s.replace('<a href="mono-specimen.html">Try Cairn Mono for code</a>','');s=s.replace('<a href="#use">Use the family</a>','<a href="#use">Use the family</a><a href="mono-specimen.html">Try Cairn Mono for code</a>');p.write_text(s)
