"""Reproducible palette quality vector; no aesthetic/medical score.
Usage: python evaluate_theme.py ../palette.json
"""
import argparse,json,math,itertools

def rgb(c):return [int(c[i:i+2],16)/255 for i in (1,3,5)]
def linear(c):return [x/12.92 if x<=.04045 else ((x+.055)/1.055)**2.4 for x in rgb(c)]
def luminance(c):return sum(x*w for x,w in zip(linear(c),[.2126,.7152,.0722]))
def contrast(a,b):
 a,b=sorted([luminance(a),luminance(b)]);return (b+.05)/(a+.05)
def oklab(c):
 r,g,b=linear(c);l=(.4122214708*r+.5363325363*g+.0514459929*b)**(1/3);m=(.2119034982*r+.6806995451*g+.1073969566*b)**(1/3);s=(.0883024619*r+.2817188376*g+.6299787005*b)**(1/3)
 return [.2104542553*l+.793617785*m-.0040720468*s,1.9779984951*l-2.428592205*m+.4505937099*s,.0259040371*l+.7827717662*m-.808675766*s]
def evaluate(p):
 pairs={role+'/'+surface:contrast(p[role],p[surface]) for role in ['fg','bold','muted','focus','red','gold','green','cyan','blue','purple'] for surface in ['bg','alt','sidebar','active_line'] if surface in p and role in p}
 accents=[(math.dist(oklab(p[a]),oklab(p[b])),a,b) for a,b in itertools.combinations(['red','gold','green','cyan','blue','purple'],2)];distance,a,b=min(accents)
 controls=None
 if 'button_face' in p:
  vals={label+'/'+state:contrast(p[label],p['button_'+state]) for label in ['button_label','button_primary_label'] for state in ['face','hover','pressed']}
  focus=min(contrast(p['focus'],p[k]) for k in ['bg','button_face','button_hover','button_pressed'])
  controls={'minimum_label_contrast':min(vals.values()),'minimum_focus_contrast':focus,'minimum_boundary_contrast':min(contrast(p['button_edge'],p[s]) for s in ['bg','alt']),'label_pairs':vals,'states':['normal','hover','pressed','focus']}
 return {'background':p['bg'],'relative_luminance':luminance(p['bg']),'nord_background_luminance_delta':abs(luminance(p['bg'])-luminance('#2e3440')),'body_contrast':contrast(p['fg'],p['bg']),'minimum_text_contrast':min(pairs.values()),'lowest_text_pair':min(pairs,key=pairs.get),'minimum_accent_oklab_distance':distance,'closest_accent_pair':[a,b],'controls':controls,'text_pairs':pairs}
if __name__=='__main__':
 parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('palette');args=parser.parse_args();data=json.load(open(args.palette));p=data.get('modes',{}).get('dark',data);print(json.dumps(evaluate(p),indent=2))
