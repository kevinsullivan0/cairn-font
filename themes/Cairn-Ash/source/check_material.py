from pathlib import Path
import json,sys,base64,re,zlib,struct,statistics
root=Path(__file__).resolve().parents[1];sys.path.insert(0,str(root/'source'));from evaluate_theme import contrast,rgb
palette=json.loads((root/'palette.json').read_text())['modes'];css=(root/'relic.css').read_text();report={}
def read_tile(name,pigment,cap):
 data=(root/'materials'/(name+'.png')).read_bytes();assert data[:8]==b'\x89PNG\r\n\x1a\n';pos=8;packed=b''
 while pos<len(data):
  n=struct.unpack('>I',data[pos:pos+4])[0];kind=data[pos+4:pos+8];chunk=data[pos+8:pos+8+n]
  if kind==b'IHDR':w,h,depth,typ,*_=struct.unpack('>IIBBBBB',chunk);assert (w,h,depth,typ)==(512,512,8,6)
  if kind==b'IDAT':packed+=chunk
  pos+=n+12
 raw=zlib.decompress(packed);alpha=[]
 for y in range(h):
  row=raw[y*(w*4+1):(y+1)*(w*4+1)];assert row[0]==0
  for x in range(w):
   r,g,b,a=row[1+x*4:5+x*4];assert r==g==b==pigment;alpha.append(a)
 assert max(alpha)<=cap and base64.b64encode(data).decode() in css
 return alpha
for mode,prefix,pigment in [('dark','basalt',0),('light','limestone',255)]:
 alpha=read_tile(prefix+'-grain',pigment,64);chrome=read_tile(prefix+'-chrome',pigment,80);p=palette[mode]
 mean_change=statistics.mean(chrome)-statistics.mean(alpha);variation=statistics.pstdev(chrome)/statistics.pstdev(alpha)
 assert abs(mean_change)<.5 and variation>1.1,(mean_change,variation)
 def composite(c,a):return '#'+''.join(f'{round(v*255*(1-a)+pigment*a):02x}' for v in rgb(c))
 max_alpha=max(max(alpha),max(chrome))/255;samples=[0,max_alpha,.045,1-(1-max_alpha)*(1-.045)];pairs={}
 for role,surfaces in [('fg',['bg','sidebar','alt','raised']),('muted',['bg','sidebar','alt']),('focus',['bg','sidebar','alt']),('button_label',['button_face','button_hover','button_pressed']),('button_primary_label',['button_face','button_hover','button_pressed'])]:
  for surface in surfaces:pairs[role+'/'+surface]=min(contrast(p[role],composite(p[surface],a)) for a in samples)
 assert min(pairs.values())>=4.5,(mode,pairs)
 report[mode]={'minimum_text_contrast':min(pairs.values()),'pairs':pairs,'texture_alpha_extrema':[min(alpha),max(alpha)],'structural_alpha_extrema':[min(chrome),max(chrome)],'structural_mean_alpha_change':mean_change,'structural_variation_ratio':variation,'reading_body_contrast_unchanged':contrast(p['fg'],p['bg'])}
assert not re.search(r'url\([\"\']?(?:https?:)?//',css)
assert not any(token in css for token in ['BASALT_GRAIN','LIMESTONE_GRAIN','BASALT_CHROME','LIMESTONE_CHROME'])
out={'method':'Conservative sRGB compositing extremes across quiet and structural pigment plus 4.5% broad wash. Black-only dark pigment and white-only light pigment. Mean opacity and variation measured from actual PNG pixels. Not a full app/plugin accessibility audit.','reading_surface':'No texture on markdown/editor/code backgrounds.','modes':report}
(root/'materials/contrast.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:{n:v[n] for n in ['minimum_text_contrast','structural_mean_alpha_change','structural_variation_ratio']} for k,v in report.items()},indent=2))
