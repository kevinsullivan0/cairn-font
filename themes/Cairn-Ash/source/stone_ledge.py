from pathlib import Path
from urllib.parse import quote
import json
root=Path(__file__).resolve().parents[1]
# The outer viewport follows the surface width; nested chip viewports stay in pixels.
profiles={
 'title':{'center_gap':34,'depth':4,'lip':1,'face':1,'chips':[
  {'anchor':.23,'width':18,'points':[[0,0],[2,.5],[4,.2],[6,1.5],[8,2.8],[11,2.2],[13,.8],[16,.4],[18,0]],'facet':[[4,.8],[6,1.5],[8,2.8],[11,2.2],[13,.8],[12,2.9],[8.5,3.6],[5.5,2.6]]},
  {'anchor':.275,'width':3,'points':[[0,0],[1.2,.9],[2,.3],[3,0]],'facet':[]},
  {'anchor':.81,'width':9,'points':[[0,4],[2,3.5],[3.5,2.3],[5.5,2.7],[7,3.7],[9,4]],'facet':[[2,3.5],[3.5,2.3],[5.5,2.7],[6,1.9],[3.3,1.7],[1,3]]}]},
 'shelf':{'depth':2,'lip':.6,'face':.4,'chips':[{'anchor':.67,'width':9,'points':[[0,0],[2,.25],[3,.8],[5,1.5],[6.5,1],[7,.3],[9,0]],'facet':[[3,.8],[5,1.5],[6.5,1],[6.7,1.6],[4.8,1.9]]}]},
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
  gap='<rect x="50%" y="0" width="34" height="4" transform="translate(-17 0)" fill="black"/>' if name=='title' else ''
  svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="100%" height="{h}"><defs><mask id="wear" maskUnits="userSpaceOnUse" x="0" y="0" width="100%" height="{h}"><rect width="100%" height="{h}" fill="white"/>{"".join(losses)}{gap}</mask></defs><g mask="url(#wear)"><rect width="100%" height="{h}" fill="{p["button_shadow"]}"/><rect width="100%" height="{lip}" fill="{iron}"/><rect y="{lip}" width="100%" height="{face}" fill="{p["button_face"]}"/></g>{"".join(facets)}</svg>'
  declarations.append(f'  --cairn-ledge-{name}: url("data:image/svg+xml,{quote(svg,safe="")}");')
 mark=f'<svg xmlns="http://www.w3.org/2000/svg" width="22" height="10" viewBox="0 0 22 10"><path d="M1 5 5 1 9 5 5 9Z M13 5 17 1 21 5 17 9Z" fill="none" stroke="{iron}" stroke-width="1"/><path d="m3 5 2-2 2 2-2 2Z m12 0 2-2 2 2-2 2Z" fill="{p['focus']}"/></svg>'
 declarations.append(f'  --cairn-divider-mark: url("data:image/svg+xml,{quote(mark,safe="")}");')
 styles.append('body.theme-'+mode+' {\n'+'\n'.join(declarations)+'\n}')
styles='\n'.join(styles)
(root/'materials/ledges.json').write_text(json.dumps({'profiles':profiles,'chip_sizing':'Nested viewports retain 3–18px widths at every component width; only positions are proportional. Outer SVG has no viewBox.','placement':'Title bottom: 4px anchor. Tab shelf: 2px seam. Vault identity: 1px seam. Exposed fracture facets are painted outside the loss mask. Only empty bands are painted; no text or focus clipping.'},indent=2)+'\n')
