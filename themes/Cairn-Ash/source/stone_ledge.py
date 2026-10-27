from pathlib import Path
from urllib.parse import quote
import json
root=Path(__file__).resolve().parents[1]
# The outer viewport follows the surface width; nested chip viewports stay in pixels.
profiles={
 'title':{'depth':4,'lip':1,'face':1,'chips':[
  {'anchor':.23,'width':12,'points':[[0,0],[2,.6],[4,.4],[6,2],[8,1.1],[10,.9],[12,0]],'facet':[[4,.9],[6,2.5],[9,1.5],[6,2]]},
  {'anchor':.81,'width':7,'points':[[0,4],[1.5,3.6],[2,2.9],[4.5,3.5],[7,4]],'facet':[]}]},
 'shelf':{'depth':2,'lip':.6,'face':.4,'chips':[{'anchor':.67,'width':5,'points':[[0,0],[1,.3],[2.5,.9],[3.2,.4],[5,0]],'facet':[]}]},
 'vault':{'depth':1,'lip':1,'face':0,'chips':[]}}
def points(values):return ' '.join(f'{x},{y}' for x,y in values)
modes=json.loads((root/'palette.json').read_text())['modes'];styles=[]
for mode,p in modes.items():
 iron='#68777d' if mode=='dark' else '#8c8374';declarations=[]
 for name,shape in profiles.items():
  h=shape['depth'];lip=shape['lip'];face=shape['face'];losses=[];facets=[]
  for chip in shape['chips']:
   position=f'x="{chip["anchor"]*100:g}%" width="{chip["width"]}" height="{h}" viewBox="0 0 {chip["width"]} {h}"'
   losses.append(f'<svg {position}><polygon points="{points(chip["points"])}" fill="black"/></svg>')
   if chip['facet']:facets.append(f'<svg {position}><polygon points="{points(chip["facet"])}" fill="{p["button_face"]}"/></svg>')
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}"><defs><mask id="wear" maskUnits="userSpaceOnUse" x="0" y="0" width="100%" height="{h}"><rect width="100%" height="{h}" fill="white"/>{"".join(losses)}</mask></defs><g mask="url(#wear)"><rect width="100%" height="{h}" fill="{p["button_shadow"]}"/><rect width="100%" height="{lip}" fill="{iron}"/><rect y="{lip}" width="100%" height="{face}" fill="{p["button_face"]}"/>{"".join(facets)}</g></svg>'
  declarations.append(f'  --cairn-ledge-{name}: url("data:image/svg+xml,{quote(svg,safe="")}");')
 styles.append('body.theme-'+mode+' {\n'+'\n'.join(declarations)+'\n}')
styles='\n'.join(styles)
(root/'materials/ledges.json').write_text(json.dumps({'profiles':profiles,'chip_sizing':'Nested viewports retain 5–12px widths at every component width; only positions are proportional. Outer SVG has no viewBox.','placement':'Title bottom: 4px anchor. Tab shelf: 2px seam. Vault identity: 1px seam. Only empty bands are painted; no text or focus clipping.'},indent=2)+'\n')
