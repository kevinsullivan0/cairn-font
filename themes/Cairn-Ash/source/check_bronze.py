from pathlib import Path
import json,sys
from check_material import read_tile
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'source'))
from evaluate_theme import contrast,rgb
palette=json.loads((root/'palette.json').read_text())['modes'];css=(root/'bronze.css').read_text();report={}
def blend(bg,fg,a):return '#'+''.join(f'{round((x*(1-a)+y*a)*255):02x}' for x,y in zip(rgb(bg),rgb(fg)))
for mode,name,pigment in [('dark','bronze-editor',(80,99,125)),('light','limestone-editor',(255,249,227))]:
 alpha=read_tile(name,pigment,32,css);p=palette[mode];base='#2e3440' if mode=='dark' else p['bg'];ink='#'+''.join(f'{v:02x}' for v in pigment)
 colors=[blend(base,ink,a/255) for a in [min(alpha),max(alpha)]]
 active=[blend(c,p['green'],.06 if mode=='dark' else .08) for c in colors];pairs={}
 for role in ['fg','muted','bold','focus','red','orange','gold','green','cyan','blue','purple','pink']:
  pairs[role+'/editor']=min(contrast(p[role],c) for c in colors)
  pairs[role+'/active_line']=min(contrast(p[role],c) for c in active)
 # Warm furniture and semantic callout text receive the same conservative checks.
 for surface in (['#3b3938','#3c3937'] if mode=='dark' else ['#e6dbc6']):
  for role in ['fg','muted','bold','focus','red','orange','gold','green','cyan','blue','purple','pink']:
   pairs[role+'/'+surface]=min(contrast(p[role],blend(surface,'#000000' if mode=='dark' else '#ffffff',a)) for a in [0,80/255])
 assert min(pairs.values())>=4.5,(mode,pairs)
 report[mode]={'base':base,'pigment':ink,'alpha_range':[min(alpha),max(alpha)],'editor_extremes':colors,'body_contrast_minimum':pairs['fg/editor'],'minimum_text_contrast':min(pairs.values()),'pairs':pairs}
assert 'background-size: 1024px 1024px' in css and '::before' not in css
(root/'materials/bronze-contrast.json').write_text(json.dumps({'scope':'Bronze only: actual background PNG alpha extrema, sRGB compositing, all text roles, active line, warm side panes and callout bodies. Semantic callout titles retain their existing colors. No texture overlay above glyphs. Code panels retain the flat base-theme surface. Not a full app/plugin accessibility audit.','modes':report},indent=2)+'\n')
print(json.dumps({k:{n:v[n] for n in ['body_contrast_minimum','minimum_text_contrast','alpha_range']} for k,v in report.items()},indent=2))
