from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
import json
from fontTools.ttLib import TTFont
from build_fonts import FlattenPen,geometry,polygons
import argparse
p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent.parent)
ROOT=p.parse_args().output;styles=['Regular','Italic','Bold','BoldItalic'];report=[]
im=Image.new('RGB',(1560,1500),'#1b1615');d=ImageDraw.Draw(im)
label=ImageFont.truetype('/System/Library/Fonts/Menlo.ttc',17) if Path('/System/Library/Fonts/Menlo.ttc').exists() else ImageFont.load_default(size=17)
d.text((35,25),'CAIRN MONO / four cuts / actual font rendering',font=label,fill='#d3ad73')
for i,style in enumerate(styles):
 fpath=ROOT/'desktop'/f'CairnMono-{style}.ttf';tt=TTFont(fpath);cm=tt.getBestCmap();gs=tt.getGlyphSet()
 assert len(cm)==114 and not any(cp>=0xe000 for cp in cm)
 assert {v[0] for v in tt['hmtx'].metrics.values()}=={1536}
 assert tt['post'].isFixedPitch==1 and tt['OS/2'].panose.bProportion==9
 assert not any(t in tt for t in ['kern','GPOS','GSUB'])
 geos={}
 for cp,name in cm.items():
  pen=FlattenPen(gs);gs[name].draw(pen);g=geometry(pen)
  if cp in [32,160]:assert g.is_empty;continue
  assert not g.is_empty and g.is_valid,(style,chr(cp),'outline')
  x0,y0,x1,y1=g.bounds
  assert x0>=89 and x1<=1447 and y0>=-600 and y1<=1800,(style,chr(cp),g.bounds)
  geos[chr(cp)]=g
 # Distinct zero/slash and recognizable counters remain open in serialized outlines.
 for ch in 'ABDOPQRabdegopq04689':
  assert sum(len(p.interiors) for p in polygons(geos[ch]))>=1,(style,ch,'counter')
 for ch in 'ij':assert len(list(polygons(geos[ch])))>=2,(style,ch,'dot')
 roundtrip=TTFont(ROOT/'web/fonts'/f'CairnMono-{style}.woff')
 assert set(tt.keys())==set(roundtrip.keys())
 for tag in tt.keys():
  if tag not in ['GlyphOrder','head']:assert tt.getTableData(tag)==roundtrip.getTableData(tag),(style,tag)
 y=85+i*345;d.text((35,y),style,font=label,fill='#d3ad73')
 font=ImageFont.truetype(str(fpath),30)
 for j,text in enumerate(['abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ','Il1|!  O0Q  rn m  [] {} ()  => != == <= >=','0123456789  .,:; \'"`  + - * / % & # @ _']):
  d.text((35,y+32+j*45),text,font=font,fill='#e3d4ba')
 for j,size in enumerate([14,16,18]):
  f=ImageFont.truetype(str(fpath),size)
  expected=size*.75
  for ch in map(chr,range(32,127)):
   assert abs(f.getlength(ch)-expected)<.02,(style,ch,'width')
  assert abs(f.getlength('AV != fn(x) -> 0;')-len('AV != fn(x) -> 0;')*expected)<.05
  d.text((35,y+225+j*30),f'{size}px   def remember(names): return [n for n in names if n != "0"]',font=f,fill='#acb28a')
 report.append(dict(style=style,advance_units=1536,character_count=len(cm),glyph_count=len(tt.getGlyphOrder()),all_cells_equal=True,no_kerning_or_ligatures=True,outline_bounds='inside cell and line metrics',counters_and_dots='passed',woff_roundtrip='passed',shaped_advance_at_px=[14,16,18]))
im.save(ROOT/'proofs/mono.png')
(ROOT/'mono-validation.json').write_text(json.dumps({'status':'passed','styles':report,'scope':'Serialized outline/metric checks and FreeType/RAQM shaping. Manual TrueType hinting is not included.'},indent=2)+'\n')
print('Mono checks passed; four-style proof saved.')
