from pathlib import Path
import base64,json,html
from fontTools.ttLib import TTFont
from reading_room import PROSE
from build_family import STYLES
ROOT=Path(__file__).resolve().parent.parent

def faces(embedded=False):
    parts=[]
    for key,weight,italic in STYLES:
        url='data:font/woff;base64,'+base64.b64encode((ROOT/'web/fonts'/f'Cairn-{key}.woff').read_bytes()).decode() if embedded else f'fonts/Cairn-{key}.woff'
        parts.append(f'''@font-face {{
  font-family: "Cairn";
  src: url("{url}") format("woff");
  font-weight: {weight};
  font-style: {'italic' if italic else 'normal'};
  font-display: swap;
  unicode-range: U+0020-007E, U+00A0, U+00A4-00A9, U+00AB, U+00BB, U+2013-2014, U+2018-2019, U+201C-201E, U+2022, U+2026, U+2212;
}}''')
    parts.append(''':root { --font-cairn: "Cairn", Georgia, "Times New Roman", serif; }
.cairn { font-family: var(--font-cairn); font-kerning: normal; font-synthesis: none; }
.cairn-prose { font-family: var(--font-cairn); font-size: 18px; line-height: 1.65; font-kerning: normal; font-synthesis: none; }
.cairn-numbers { font-variant-numeric: tabular-nums; }
''')
    return '\n\n'.join(parts)

PAGE='''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cairn — First edition</title>
FONT_LOAD
<style>
:root{--paper:#f7f3e9;--card:#fffcf5;--ink:#253032;--quiet:#66695d;--rule:#c9c5b4;--accent:#84633d;--size:18px;--leading:1.65}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:15px/1.5 system-ui,sans-serif}body.dark{--paper:#172024;--card:#232e31;--ink:#eee6d5;--quiet:#bab9ac;--rule:#56615f;--accent:#d5b47e}main{max-width:1160px;margin:auto;padding:40px 28px 80px}a{color:var(--accent);text-underline-offset:4px}header{border-top:6px solid var(--ink);padding-top:23px}.eyebrow{text-transform:uppercase;font-size:11px;letter-spacing:.17em;font-weight:650;color:var(--accent)}h1{font:400 clamp(55px,9vw,112px)/1.1 var(--font-cairn);margin:28px 0 17px}.deck{max-width:670px;color:var(--quiet);font-size:17px}.tools{display:flex;gap:20px;flex-wrap:wrap;align-items:center;border-block:1px solid var(--rule);margin:30px 0;padding:17px 0}.tools label{display:flex;align-items:center;gap:9px;font-size:13px}button,select,textarea{font:inherit;color:var(--ink);background:var(--card);border:1px solid var(--rule);border-radius:3px;padding:9px 12px}button{cursor:pointer}button:hover{border-color:var(--accent)}input{accent-color:var(--accent)}:focus-visible{outline:2px solid var(--accent);outline-offset:4px}.subhead{font-size:12px;letter-spacing:.10em;text-transform:uppercase;margin:35px 0 17px;color:var(--quiet)}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px}.card{background:var(--card);border:1px solid var(--rule);padding:24px;min-width:0}.label{font:12px/1.5 system-ui,sans-serif;color:var(--quiet);display:flex;justify-content:space-between}.type{font-family:var(--font-cairn);font-size:var(--size);line-height:var(--leading);font-synthesis:none;font-kerning:normal}.card .headline{font:inherit;font-size:1.65em;line-height:1.3;margin:18px 0}.sample{white-space:pre-wrap;overflow-wrap:anywhere}.alphabet{font-size:22px;line-height:1.7;overflow-wrap:anywhere;border-top:1px solid var(--rule);padding-top:18px;margin-top:21px}.regular{font-weight:400;font-style:normal}.italic{font-weight:400;font-style:italic}.bold{font-weight:700;font-style:normal}.bolditalic{font-weight:700;font-style:italic}.note{font-size:13px;color:var(--quiet)}details{margin:22px 0}summary{cursor:pointer;color:var(--accent)}textarea{margin-top:15px;width:100%;min-height:110px;line-height:1.5}.reading{display:grid;grid-template-columns:minmax(0,1.35fr) minmax(0,1fr);gap:34px;margin-top:25px}.essay{max-width:65ch}.essay h2{font-size:1.8em;line-height:1.25;margin:0 0 16px}.essay p{margin:0 0 1.2em}.essay .lead{color:var(--quiet);font-style:italic;margin-bottom:25px}.side{align-self:start;border-top:3px solid var(--ink);padding-top:20px}.side h2{font-size:1.4em;margin:0 0 20px}.row{padding:20px 0;border-bottom:1px solid var(--rule)}.row small{display:block;font-size:.8em;color:var(--quiet);margin-top:8px}.quote{padding:24px;background:var(--ink);color:var(--paper);margin-top:25px;font-style:italic}.quote strong{font-weight:700}.numbers{font-variant-numeric:tabular-nums;font-size:16px}.numbers div{display:flex;justify-content:space-between;gap:20px;padding:8px 0}.install{margin-top:45px;border-top:1px solid var(--rule);padding-top:15px}.links{display:flex;gap:16px;flex-wrap:wrap}.ornaments{font-size:40px;letter-spacing:.12em}.status{font-size:12px;color:var(--quiet)}code{font-family:ui-monospace,monospace;font-size:12px}.symbol-proof{font-size:25px;overflow-wrap:anywhere;padding:16px 0}footer{border-top:1px solid var(--rule);padding-top:22px;margin-top:40px}.proof{max-width:100%;display:block}
@media(max-width:800px){main{padding:25px 17px 50px}.grid,.reading{grid-template-columns:1fr}.card{padding:19px}.tools{gap:14px}.alphabet{font-size:20px}}@media print{.tools,details,.install{display:none}body{background:white}.grid{break-inside:avoid}a{color:inherit}}
</style></head><body><main>
<header><div class="eyebrow">Cairn / First edition / Personal font family</div><h1>What the stone<br>remembers</h1><p class="deck">Cut crowns, deep bowls, and edges that catch the light. Four voices for the same old stone: Regular, Italic, Bold, and Bold Italic.</p><p class="status" id="font-status" role="status">Loading the four font styles…</p></header>
<div class="tools"><label for="size">Text size <input id="size" type="range" min="12" max="28" value="18"><output id="size-label">18 px</output></label><label for="leading">Line spacing <select id="leading"><option value="1.5">1.5</option><option value="1.65" selected>1.65</option><option value="1.8">1.8</option></select></label><button id="theme" aria-pressed="false">Use dark paper</button><a href="#use">Use the family</a></div>
<h2 class="subhead">Four cuts, one family</h2><div class="grid">STYLE_CARDS</div>
<details><summary>Try your own text in all four styles</summary><label for="sample-input" class="note">Sample text</label><textarea id="sample-input">At the broken gate, a keeper waits for the last name. The rain has worn the steps; the letters still hold their edges.</textarea><p class="note" id="coverage" aria-live="polite"></p></details>
<h2 class="subhead">In use / prose and an archive</h2><div class="reading"><article class="essay type cairn"><h2>Names outlast the walls</h2><p class="lead">A record of the last watch</p>PROSE</article><aside class="side type cairn"><h2>The Archive</h2><div class="note">Library / Field notes / Recent</div><div class="row"><strong>The northern road</strong><small>Chapter 03 / Last read at 08:45</small></div><div class="row"><strong>A record of names</strong><small>Field notes / Saved yesterday</small></div><div class="row"><strong>The last watch</strong><small>Chapter 12 / 24 pages remaining</small></div><blockquote class="quote">“We can keep the record,” he said, “even when we cannot <strong>explain it</strong>.”</blockquote><h3 class="subhead">Tabular figures</h3><div class="numbers"><div><span>First watch</span><span>01:11</span></div><div><span>Last watch</span><span>08:48</span></div><div><span>Names recorded</span><span>1,288</span></div></div></aside></div>
<details><summary>Punctuation and carved parentheses</summary><div class="symbol-proof cairn">“ ” ‘ ’ „ , . : ; ! ? … — – − + = / \\ | ¦ ( ) [ ] { } &lt; &gt; @ # $ % &amp; * ^ _ ` ~ • ¤ ¥ § ¨ © « »</div><p class="note">All glyphs in this family are drawn for Cairn. Parentheses have curved middles and sharp, cut ends. No inherited ornaments are included.</p></details>
<section id="use" class="install"><h2>Use Cairn</h2><p>For HTML, copy the <code>web</code> folder beside your page and link <code>web/cairn.css</code>. Use <code>class="cairn-prose"</code> on a reading section. Ordinary <code>&lt;strong&gt;</code> and <code>&lt;em&gt;</code> select the real styles.</p><p>For desktop apps, the four TrueType files share one family name: <strong>Cairn</strong>. Nothing is installed by this page.</p><p class="links">PACKAGE_LINKS</p><p class="note">A useful starting point: 18 px for prose, 16 px for interface text, with 1.6–1.7 line spacing. The 12–14 px specimens are stress tests. Accent letters and other scripts use your fallback font.</p></section>
<footer><p class="note">A personal edition, October 2026. New prose, alphabet, figures, and punctuation. All glyph outlines are generated from the included Cairn drawing source. No inherited ornaments remain. Native raster proofs and serialized font checks accompany the family.</p></footer>
</main><script>
const supported=new Set(COVERAGE),input=document.getElementById('sample-input');
function updateSample(){for(const el of document.querySelectorAll('.sample'))el.textContent=input.value;const missing=[...new Set([...input.value].filter(c=>!supported.has(c.codePointAt(0))&&!/\\s/.test(c)))];document.getElementById('coverage').textContent=missing.length?'Fallback font used for: '+missing.join(' '):'Every character in this sample is drawn by Cairn.';}
input.addEventListener('input',updateSample);updateSample();
document.getElementById('size').addEventListener('input',e=>{document.documentElement.style.setProperty('--size',e.target.value+'px');document.getElementById('size-label').textContent=e.target.value+' px';});
document.getElementById('leading').addEventListener('change',e=>document.documentElement.style.setProperty('--leading',e.target.value));
document.getElementById('theme').addEventListener('click',()=>{const dark=document.body.classList.toggle('dark');document.getElementById('theme').setAttribute('aria-pressed',String(dark));document.getElementById('theme').textContent=dark?'Use light paper':'Use dark paper';});
if(document.fonts&&document.fonts.load){Promise.all(['normal 400','italic 400','normal 700','italic 700'].map(s=>document.fonts.load(s+' 18px "Cairn"'))).then(loaded=>{document.getElementById('font-status').textContent=loaded.every(f=>f.length)?'All four Cairn styles are loaded. No installation needed.':'Some font styles did not load. Open the standalone specimen instead.';}).catch(()=>{document.getElementById('font-status').textContent='Font files could not load. Open the standalone specimen instead.';});}else{document.getElementById('font-status').textContent='Font loading status is unavailable in this viewer.';}
</script></body></html>'''

def build():
    (ROOT/'web/cairn.css').write_text(faces())
    (ROOT/'web/cairn-embedded.css').write_text(faces(True))
    cards=[]
    for key,weight,italic in STYLES:
        name='Bold Italic' if key=='BoldItalic' else key
        cards.append(f'<section class="card"><div class="label"><span>{name}</span><span>{weight} / {"italic" if italic else "upright"}</span></div><div class="type {key.lower()}"><h3 class="headline">The last light on stone</h3><p class="sample"></p><div class="alphabet">abcdefghijklmnopqrstuvwxyz<br>ABCDEFGHIJKLMNOPQRSTUVWXYZ<br>0123456789 / Il1 O0 rn m</div></div></section>')
    prose=''.join('<p>'+html.escape(p)+'</p>' for p in PROSE.split('\n\n'))
    cm=TTFont(ROOT/'desktop/Cairn-Regular.ttf').getBestCmap()
    page=PAGE.replace('STYLE_CARDS',''.join(cards)).replace('PROSE',prose).replace('COVERAGE',json.dumps(sorted(cm)))
    links='<a href="README.html">Quick start and desktop instructions</a><a href="proofs/family.png">Family proof</a><a href="proofs/small-text.png">Small text proof</a>'
    (ROOT/'specimen.html').write_text(page.replace('FONT_LOAD','<style>'+faces(True)+'</style>').replace('PACKAGE_LINKS',links))
    (ROOT/'web/example.html').write_text(page.replace('FONT_LOAD','<link rel="stylesheet" href="cairn.css">').replace('PACKAGE_LINKS','<a href="../specimen.html">Standalone specimen</a><a href="../README.html">Quick start</a>'))

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('root',type=Path,nargs='?',default=ROOT)
    ROOT=p.parse_args().root;build()
