"""The Hours of Bellweather Reach. Repaint one panel or the whole quadriptych.

python3 paint_hours.py all  # Pillow, a local C++17 compiler; no external imagery
python3 paint_hours.py evening --width 400 --out /tmp/paint-proof
"""
from argparse import ArgumentParser
from array import array
import ctypes as ct
from dataclasses import dataclass
from functools import lru_cache
from hashlib import sha256
from math import atan2, cos, exp, floor, hypot, pi, sin, sqrt
from pathlib import Path
from random import Random
import subprocess
import sys
from tempfile import gettempdir, TemporaryDirectory
from PIL import Image

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
from raster import Canvas, mix, smooth

PHASES = ('morning', 'afternoon', 'evening', 'night')
# Palette entries are local material hues in unfiltered daylight.
PALETTE = {
    'cliff': (139, 126, 104), 'lichen': (149, 148, 103), 'talus': (104, 111, 104),
    'grass': (127, 139, 85), 'grasslit': (167, 161, 97), 'pine': (63, 88, 69),
    'cypress': (61, 84, 64), 'silverleaf': (117, 136, 97), 'stone': (193, 177, 139),
    'dressed': (213, 195, 154), 'ruin': (170, 165, 139), 'slate': (111, 124, 115),
    'tile': (162, 106, 75), 'recess': (63, 66, 57), 'iron': (79, 79, 62),
    'wood': (108, 79, 57), 'brass': (191, 154, 77), 'sail': (192, 104, 61),
    'canvas': (221, 199, 154), 'lamp': (252, 194, 92),
}

@lru_cache(None)
def noise(x, y, seed):
    bits = (x*0x9e3779b9 + y*0x85ebca6b + seed*0xc2b2ae35) & 0xffffffff
    bits = ((bits^(bits>>16))*0x7feb352d) & 0xffffffff
    bits = ((bits^(bits>>15))*0x846ca68b) & 0xffffffff
    return (bits^(bits>>16))/0xffffffff

def field(x,y,s):
    i,j=floor(x),floor(y)
    u,v=smooth(x-i),smooth(y-j)
    return ((1-u)*noise(i,j,s)+u*noise(i+1,j,s))*(1-v)+((1-u)*noise(i,j+1,s)+u*noise(i+1,j+1,s))*v

def native():
    src=HERE/'oil.cpp'
    binary=Path(gettempdir())/('cairn-oil-'+sha256(src.read_bytes()).hexdigest()[:20]+'.so')
    if not binary.is_file():
        with TemporaryDirectory(dir=binary.parent) as staging:
            plugin=Path(staging)/'oil.so'
            subprocess.run(['c++','-std=c++17','-O3','-shared','-fPIC',str(src),'-o',str(plugin)],check=True)
            plugin.replace(binary)
    lib=ct.CDLL(str(binary))
    lib.atmosphere.argtypes=[ct.c_void_p,ct.c_int,ct.c_int,ct.c_int]
    lib.spans.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_int,ct.c_int,ct.c_void_p,ct.c_int]
    lib.crossing_clouds.argtypes=[ct.c_void_p,ct.c_void_p,ct.c_int,ct.c_int,ct.c_int]
    lib.shadows.argtypes=lib.crossing_clouds.argtypes
    lib.paint.argtypes=[ct.c_void_p,ct.c_int,ct.c_int,ct.c_int]
    return lib

# Translate a day/sunset/moonlight illumination and hemispheric sky fill into oil colours.
ILLUM = (
    ((1.12,.99,.78),(.58,.69,.77),(165,163,143),-.85,.40,.51),
    ((1.04,1.02,.88),(.51,.65,.73),(149,174,175),.66,-.17,.80),
    ((1.26,.83,.52),(.53,.55,.68),(169,134,131),-.92,-.18,.34),
    ((.57,.68,.77),(.28,.39,.50),(82,109,126),.68,-.42,.63),
)

class OilCanvas(Canvas):
    """The original Canvas pixel store plus depth-aware landscape and oil-brush passes."""
    def __init__(self,w,h,phase):
        super().__init__(w,h)
        self.phase=phase
        self.lib=native()
        self.buffer=(ct.c_ubyte*len(self.pixels)).from_buffer(self.pixels)
        self.depth=(ct.c_float*(w*h))()
        ct.memset(self.depth,0,ct.sizeof(self.depth))
        self.lib.atmosphere(self.buffer,w,h,phase)
        self.tris=array('f')
    def flush(self):
        if self.tris:
            self.lib.spans(self.buffer,self.depth,self.width,self.height,self.tris.buffer_info()[0],len(self.tris)//20)
            self.tris=array('f')
    def finish(self):
        self.flush()
        self.lib.paint(self.buffer,self.width,self.height,811+self.phase)

@dataclass
class View:
    cx:float
    cy:float
    scale:float
    turn:float
    tilt:float
    depth:float
    fog:float

class Scene:
    def __init__(self,board,view,seed):
        self.board,self.view,self.seed=board,view,seed
        self.sn,self.cs=sin(view.turn),cos(view.turn)
        self.st,self.ct=sin(view.tilt),cos(view.tilt)
        self.light,self.fill,self.air,self.lx,self.ld,self.lz=ILLUM[board.phase]
    def project(self,p):
        x,y,z=p;v=self.view
        sx=x*self.cs-y*self.sn
        d=x*self.sn+y*self.cs
        return (v.cx+v.scale*sx,v.cy+v.scale*(d*self.st-z*self.ct)/3.5,v.depth+v.scale*(d*self.ct+z*self.st))
    def face(self,points,pigment,material=0,adjust=1,uv=None,seed=None):
        if len(points)<3:return
        a,b,c=points[:3]
        i,j,k=(b[n]-a[n] for n in range(3));l,m,o=(c[n]-a[n] for n in range(3))
        nx,ny,nz=j*o-k*m,k*l-i*o,i*m-j*l
        length=sqrt(nx*nx+ny*ny+nz*nz)+1e-8
        nx,ny,nz=nx/length,ny/length,nz/length
        sx=nx*self.cs-ny*self.sn;sd=nx*self.sn+ny*self.cs
        strength=max(0,sx*self.lx+sd*self.ld+nz*self.lz)
        sky=.88+.14*max(0,nz)-.095*max(0,-nz)
        raw=PALETTE.get(pigment,pigment)
        color=tuple(raw[n]*(self.fill[n]*sky+(self.light[n]-self.fill[n])*(strength**.71))*adjust for n in range(3))
        if pigment=='lamp':color=(255,202,112)
        color=mix(color,self.air,self.view.fog)
        if uv is None:
            uv=[(x if abs(ny)>abs(nx) else y,z) if abs(nz)<.65 else (x,y) for x,y,z in points]
        vertices=[(*self.project(p),*v) for p,v in zip(points,uv)]
        tail=(*color,material,self.seed if seed is None else seed)
        for i in range(1,len(vertices)-1):
            self.board.tris.extend((*vertices[0],*vertices[i],*vertices[i+1],*tail))

def island(s,rx,ry,drop,seed,grassy=True):
    # A jointed upthrust slab. Vertically persistent faults, weathered shelves and offset
    # bottom spurs preserve geological continuity as the profile narrows into the air.
    rng=Random(seed);sectors=114;angles=[2*pi*(i+rng.uniform(-.31,.31))/sectors for i in range(sectors)]
    ridge=[(.42,.35),(.73,.21),(.88,.12),(.97,.04),(1.,-.03),(.96,-.11),(.99,-.16),(.93,-.22),
           (.94,-.28),(.84,-.39),(.82,-.44),(.79,-.53),(.64,-.61),(.68,-.65),(.49,-.75),(.41,-.82),(.24,-.88),(.07,-.92)]
    layers=[]
    def top_at(x,y):
        return 1.18+1.18*field(x*.11+7,y*.14,seed)+.48*sin(.24*x+.18*y)
    for row,(radius,lev) in enumerate(ridge):
        ring=[]
        for i,ang in enumerate(angles):
            ca,sa=cos(ang),sin(ang)
            border=.90+.11*sin(3*ang+seed*.41)+.067*sin(5*ang+seed*.073)+.049*sin(8*ang-seed*.094)+.085*(field(4*ca,4*sa,seed)-.5)
            fracture=field(ca*9+.5*lev,sa*9+.85*lev,seed+4)
            flare=radius*(border+.075*(fracture-.5)+.036*(field(i*.45,row*.46,seed+9)-.5))
            x=rx*(ca*flare+.17*sin(seed*.09)*max(0,-lev));y=ry*(sa*flare+.16*cos(seed*.18)*max(0,-lev))
            thickness=1+.15*cos(ang*3+seed*.25)+.15*sin(ang*5+seed*.081)+.25*(fracture-.5)
            z=top_at(x,y)*(1-min(1,max(0,-lev*2)))+min(0,lev)*drop*thickness
            if lev>0:z-=max(0,radius-.7)*3
            z+=min(1,max(0,-lev*6))*1.5*(field(i*.16,row*.37,seed)-.5)
            ring.append((x,y,z))
        layers.append(ring)
    core=(0,0,top_at(0,0))
    for i in range(sectors):
        n=(i+1)%sectors
        s.face([core,layers[0][i],layers[0][n]],'grass' if grassy else 'cliff',2)
    for row,(a,b) in enumerate(zip(layers,layers[1:])):
        for i in range(sectors):
            n=(i+1)%sectors
            patch=field(cos(angles[i])*4,sin(angles[i])*4+.75*row,seed+17)
            if row<3 and grassy:
                pigment=mix(PALETTE['grass'],PALETTE['grasslit'],patch*.64);material=2
            else:
                pigment=mix(PALETTE['cliff'],PALETTE['talus'],.67*patch+.15*(row>7));material=1
                if row in (4,7,11) and patch>.55:pigment=mix(pigment,PALETTE['lichen'],patch*.3)
            # The discrete facets are modulated by strata and a continuous mineral field.
            tint=.97+.082*(patch-.5)
            for tri in ([a[i],b[i],b[n]],[a[i],b[n],a[n]]):
                uvs=[(.63*x+.62*y,z) for x,y,z in tri] if row>=3 else None
                s.face(tri,pigment,material,tint,uvs,seed)
    return top_at

def box(s,x,y,z,w,d,h,pig='stone',material=3):
    p=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z)]
    q=[(a,b,c+h) for a,b,c in p]
    for i in range(4):
        j=(i+1)%4;s.face([p[i],p[j],q[j],q[i]],pig,material)
    s.face(q,pig,material)

def roof(s,x,y,z,w,d,h,pig='tile',hip=.62):
    p=[(x-w/2,y-d/2,z),(x+w/2,y-d/2,z),(x+w/2,y+d/2,z),(x-w/2,y+d/2,z)]
    l=(x-max(.01,w/2*(1-hip)),y,z+h);r=(2*x-l[0],y,z+h)
    s.face([p[0],p[1],r,l],pig,4);s.face([p[1],p[2],r],pig,4)
    s.face([p[2],p[3],l,r],pig,4);s.face([p[3],p[0],l],pig,4)

def arch(s,x,y,z,w,h,axis,side,lit=False):
    # Pointed round-headed aperture expressed in wall coordinates.
    r=w/2;spring=h-r
    coords=[(-r,0),(r,0),(r,spring)]+[(r*cos(pi*j/12),spring+r*sin(pi*j/12)) for j in range(1,13)]
    def loc(u,v,offset=0):
        return (x+u,y+offset*side,z+v) if axis==0 else (x+offset*side,y+u,z+v)
    orient=side*(1 if axis==0 else -1)
    if orient>0:coords.reverse()
    s.face([loc(u,v) for u,v in coords],'lamp' if lit else 'recess',0,.91)
    if w<.42:return
    for j in range(9):
        a,b=pi*j/9,pi*(j+1)/9
        vals=[(r*cos(a),spring+r*sin(a)),((r+.13)*cos(a),spring+(r+.13)*sin(a)),
              ((r+.13)*cos(b),spring+(r+.13)*sin(b)),(r*cos(b),spring+r*sin(b))]
        if orient>0:vals.reverse()
        s.face([loc(u,v,.002) for u,v in vals],'dressed',3,1.01 if j%3 else .94)

def walls(s,x,y,z,w,d,h,pig='stone',windows=3):
    box(s,x,y,z,w,d,h,pig)
    for side in (-1,1):
        for i in range(windows):
            u=(i-(windows-1)/2)*w/(windows+.45)
            arch(s,x+u,y+side*(d/2+.013),z+h*.47,min(w/(windows+2)*.46,.73),h*.39,0,side,
                 s.board.phase==3 and (i+int(x)+side)%4==0)
        for i in range(2):
            arch(s,x+side*(w/2+.013),y+(i-.5)*d*.41,z+h*.43,min(.65,d*.16),h*.42,1,side,
                s.board.phase==3 and (int(y)+i)%4==0)
    box(s,x,y,z+h-.18,w+.19,d+.19,.21,'dressed')
    # Each building has a ground entrance, raised threshold, sash recesses and coping.
    for side in (-1,1):
        ex=x-w*.24;wy=y+side*(d*.5+.026)
        arch(s,ex,wy,z,min(.82,w*.28),min(1.82,h*.62),0,side)
        box(s,ex,wy+side*.13,z+.09,min(1.0,w*.37),.36,.17,'dressed')
        for j in range(windows):
            xx=x+(j-(windows-1)/2)*w/(windows+.45)
            box(s,xx,wy,z+h*.46,min(.95,w/(windows+1)*.85),.13,.13,'dressed')
            if j%3==1 and w>2.1:
                box(s,xx-.34,wy,z+h*.48,.17,.095,h*.31,'slate',4)
    if windows>1:
        box(s,x+w*.29,y-.11*d,z+h+.24,.37,.39,.91,'stone')
        box(s,x+w*.29,y-.11*d,z+h+1.12,.49,.50,.16,'tile')


def tower(s,x,y,z,w,h):
    d=w*.89
    walls(s,x,y,z,w,d,h*.50,windows=1)
    box(s,x,y,z+h*.50,w*.91,d*.92,h*.30)
    for side in (-1,1):
        arch(s,x,y+side*(d*.46+.012),z+h*.58,w*.14,h*.13,0,side)
    clockface(s,x,y,z+h*.39,.59,w)
    level=z+h*.80
    box(s,x,y,level,w+.28,d+.28,.33,'dressed')
    # Open lantern with deep double arches; air is actually visible through it.
    rise=h*.19
    for a in (-1,1):
        for b in (-1,1):
            box(s,x+a*(w*.5-.22),y+b*(d*.5-.22),level+.30,.44,.44,rise)
    for axis,L,D in ((0,w,d),(1,d,w)):
        for side in (-1,1):
            for off in (-.25,.25):
                opa=L*.204
                for j in range(12):
                    pts=[]
                    for a,top in ((j/12,False),((j+1)/12,False),((j+1)/12,True),(j/12,True)):
                        theta=pi*(1-a)
                        u=L*off+opa*cos(theta);v=rise+.31 if top else rise-.38+opa*sin(theta)
                        pts.append((x+u,y+side*D*.5,level+v) if axis==0 else (x+side*D*.5,y+u,level+v))
                    if side*(1 if axis==0 else -1)>0:pts.reverse()
                    s.face(pts,'dressed',3)
            if axis==0:box(s,x,y+side*(d*.5-.14),level+.26,.25,.28,rise-.24,'dressed')
            else:box(s,x+side*(w*.5-.14),y,level+.26,.28,.25,rise-.24,'dressed')
    # Bell hung below its crossbeam, and corbels casting distinct shadows beneath the lantern.
    box(s,x,y,level+rise-.04,w*.77,.18,.27,'wood')
    box(s,x,y,level+rise-.5,.085,.09,.50,'iron')
    bell=[]
    for dz,rad in ((0,.34),(.07,.37),(.19,.26),(.48,.18),(.56,.05)):
        bell.append([(x+rad*cos(j*pi/6),y+rad*sin(j*pi/6),level+rise-.94+dz) for j in range(12)])
    for lo,hi in zip(bell,bell[1:]):
        for j in range(12):
            n=(j+1)%12;s.face([lo[j],lo[n],hi[n],hi[j]],'brass')
    for side in (-1,1):
        for j in (-1,0,1):
            box(s,x+w*.35*j,y+side*d*.49,level-.23,.19,.31,.50,'dressed')
    cap=level+rise+.33
    box(s,x,y,cap,w+.29,d+.29,.30,'dressed')
    roof(s,x,y,cap+.30,w+.68,d+.68,w*.84,'slate',.92)
    box(s,x,y,cap+.30+w*.83,.08,.08,.83,'brass',0)

def chapel(s,x,y,z):
    # The long copper-roofed nave meets a taller apse and a family of low stone dependencies.
    walls(s,x,y,z,6.5,2.8,3.25,windows=5)
    roof(s,x,y,z+3.25,6.93,3.22,1.45,'tile',.16)
    for i in range(5):
        for side in (-1,1):
            box(s,x-2.8+i*1.42,y+side*1.52,z,.29,.48,2.84,'ruin')
    for dx,dy,w,d,h in ((-3.24,-1.2,2.45,1.83,2.5),(2.15,-2.45,3.74,2.9,3.62),
                         (-1.86,2.44,3.95,1.83,1.85),(.84,2.30,1.9,1.55,2.56)):
        walls(s,x+dx,y+dy,z,w,d,h,windows=max(1,int(w*.65)))
        roof(s,x+dx,y+dy,z+h,w+.28,d+.31,d*.36,'slate' if dy<0 else 'tile',.30)

def bridge(s,x,y,z,length,arches,depth=1.2):
    # Stone viaduct across the lip of the island, built around real arched voids.
    L=length/arches;r=L*.41; low=z-3.75
    for k in range(arches):
        u=x+L*(k+.5)
        for j in range(17):
            a,b=pi*(1-j/17),pi*(1-(j+1)/17)
            x1,x2=u+r*cos(a),u+r*cos(b);v1,v2=low+r*sin(a),low+r*sin(b)
            for side in [-1,1]:
                pts=[(x1,y+side*depth*.5,v1),(x2,y+side*depth*.5,v2),(x2,y+side*depth*.5,z),(x1,y+side*depth*.5,z)]
                if side>0:pts.reverse()
                s.face(pts,'stone',3)
                pts=[(x1,y+side*(depth*.5+.004),v1),(x2,y+side*(depth*.5+.004),v2),
                     (u+(r+.15)*cos(b),y+side*(depth*.5+.004),low+(r+.15)*sin(b)),
                     (u+(r+.15)*cos(a),y+side*(depth*.5+.004),low+(r+.15)*sin(a))]
                if side>0:pts.reverse()
                s.face(pts,'dressed',3,.96 if j%2 else 1.04)
            s.face([(x1,y-depth*.5,v1),(x2,y-depth*.5,v2),(x2,y+depth*.5,v2),(x1,y+depth*.5,v1)][::-1],'ruin',3,.83)
    for k in range(arches+1):
        for wid,yoff,base,dz in ((L-2*r,0,low-3.0,z-low+3.0),(.51,.04,low-1.4,1.9)):
            box(s,x+k*L,y+yoff,base,wid,depth+.25,dz,'ruin')
    box(s,x+length*.5,y,z,length+.30,depth+.20,.19,'dressed')
    for side in (-1,1):
        box(s,x+length*.5,y+side*depth*.52,z+.16,length+.32,.17,.41,'ruin')

def tree(s,x,y,z,height,rng,kind='cypress'):
    if height<.45:return
    radius=height*(.115 if kind=='cypress' else .245)
    lean=height*rng.uniform(-.10,.055);spin=rng.random()*6
    box(s,x,y,z,.06*height,.06*height,height*.64,'wood',0)
    # Interlocking crowns split in the direction of growth. Each crown shares its edges.
    for clump in range(4 if kind=='cypress' else 7):
        if clump:
            ang=clump*2.40+spin
            off=radius*rng.uniform(.22,.79)
            dx,dy=off*cos(ang),off*sin(ang)
            start=rng.uniform(.17,.40);length=rng.uniform(.33,.64);wid=radius*rng.uniform(.4,.77)
        else: dx=dy=0;start=.16;length=.84;wid=radius*.87
        rings=[]
        for t,r in ((0,.03),(.21,.79),(.45,1),(.72,.71),(.9,.36),(1,.02)):
            ring=[]
            for j in range(7):
                a=2*pi*j/7+spin;amount=r*wid*rng.uniform(.8,1.12)
                ring.append((x+dx+lean*(start+length*t)**1.5+amount*cos(a),y+dy+amount*sin(a),z+height*(start+length*t)+(.04*height*rng.uniform(-1,1) if r>.1 else 0)))
            rings.append(ring)
        for low,high in zip(rings,rings[1:]):
            for i in range(7):
                j=(i+1)%7;s.face([low[i],low[j],high[j],high[i]],kind,2,rng.uniform(.90,1.12))

def vegetation(s,top,rx,ry,seed,density,fore=False):
    rng=Random(seed)
    # Windward exposures carry open grass. Clusters gather at sheltered corners.
    for _ in range(density):
        ang=rng.uniform(0,2*pi);rad=sqrt(rng.random())*.83
        x=rx*rad*cos(ang);y=ry*rad*sin(ang)
        if not fore and -8<x<7 and -4.4<y<4.4:continue
        if field(x*.19,y*.19,seed+29)<.34:continue
        h=rng.uniform(.50,2.08)*(1.25 if fore else 1)
        tree(s,x,y,top(x,y)-.11,h,rng,'silverleaf' if rng.random()<.43 else 'cypress')

def crag(s,x,y,z,rx,ry,drop,seed):
    rng=Random(seed);rings=[];N=13
    wav=[rng.uniform(.80,1.22) for i in range(N)]
    for v,wd in ((0,.54),(-.05,.84),(-.13,1),(-.33,.91),(-.40,.94),(-.64,.76),(-.78,.53),(-1,.07)):
        ring=[]
        for i in range(N):
            ang=i*2*pi/N;amount=wd*wav[i]*rng.uniform(.87,1.05)
            ring.append((x+rx*(amount*cos(ang)+.28*v),y+ry*amount*sin(ang),
                         z+v*drop+rx*.31*sin(2*ang+.65)+rng.uniform(-.15,.15)))
        rings.append(ring)
    s.face(rings[0],'lichen',2)
    for top,btm in zip(rings,rings[1:]):
        for j in range(N):
            n=(j+1)%N
            for pts in ([top[j],btm[j],btm[n]],[top[j],btm[n],top[n]]):
                s.face(pts,'cliff',1,rng.uniform(.92,1.08),[(.68*a+.56*b,c) for a,b,c in pts])

def dome(s,x,y,z,rad):
    rings=[];N=18
    for lev,wd in ((0,1.0),(2.2,1.0),(2.27,1.08),(2.45,1.09),(2.5,1.02),
                   (2.82,.97),(3.15,.84),(3.46,.59),(3.69,.29),(3.76,.08)):
        rings.append([(x+rad*wd*cos(2*pi*i/N),y+rad*wd*sin(2*pi*i/N),z+lev) for i in range(N)])
    for k,(low,top) in enumerate(zip(rings,rings[1:])):
        for j in range(N):
            n=(j+1)%N
            s.face([low[j],low[n],top[n],top[j]],'stone' if k<4 else 'slate',3 if k<4 else 4,
                   .95 if k>=4 and j%3==0 else 1)
    box(s,x,y,z+3.69,.29,.29,.44,'brass')
    roof(s,x,y,z+4.09,.48,.48,.36,'slate',1.)

def limb(s,a,b,ra,rb):
    ax,ay,az=a;bx,by,bz=b
    rings=[]
    dx,dy,dz=bx-ax,by-ay,bz-az
    n=hypot(dx,dy)
    ux,uy=(dy/n,-dx/n) if n>.001 else (1.,0.)
    L=sqrt(dx*dx+dy*dy+dz*dz)+1e-8
    vx,vy,vz=-dz*uy/L,dz*ux/L,(dx*uy-dy*ux)/L
    for p,r in ((a,ra),(b,rb)):
        ring=[]
        for j in range(6):
            co,si=cos(2*pi*j/6),sin(2*pi*j/6)
            ring.append((p[0]+r*(co*ux+si*vx),p[1]+r*(co*uy+si*vy),p[2]+r*si*vz))
        rings.append(ring)
    low,hi=rings
    for i in range(6):
        j=(i+1)%6;s.face([low[i],low[j],hi[j],hi[i]],'wood',1)

def pine(s,x,y,z,h,seed):
    # Weather-bent pine built from the branching scaffold outwards, with grouped needle pads.
    rng=Random(seed);lean=rng.choice((-1,1))
    def loc(p):return (x+p[0]*h,y+p[1]*h,z+p[2]*h)
    def crown(p,w,ht):
        N=12;rings=[];hue=mix(PALETTE['pine'],PALETTE['silverleaf'],rng.uniform(.06,.32))
        for t,r in ((-.45,.27),(-.28,.77),(.02,1),(.33,.66),(.51,.13)):
            ring=[]
            for j in range(N):
                ang=2*pi*j/N;rad=w*r*rng.uniform(.80,1.18)
                ring.append(loc((p[0]+rad*cos(ang),p[1]+.74*rad*sin(ang),p[2]+ht*(t+rng.uniform(-.09,.09)))))
            rings.append(ring)
        for lo,hi in zip(rings,rings[1:]):
            for j in range(N):
                n=(j+1)%N;s.face([lo[j],lo[n],hi[n],hi[j]],hue,2,rng.uniform(.92,1.10))
    trunk=[(0,0,0),(.043*lean,.007,.19),(.035*lean,.026,.36),
           (.138*lean,.024,.61),(.178*lean,.012,.77),(.16*lean,.053,.92)]
    for j,(a,b) in enumerate(zip(trunk,trunk[1:])):limb(s,loc(a),loc(b),h*(.035-.0051*j),h*(.031-.0051*j))
    for k in range(17):
        base=trunk[2+k%4];ang=k*2.399+seed*.44;length=rng.uniform(.19,.38)*(1.21-base[2]*.41)
        dx,dy=length*cos(ang)+.035*lean,length*sin(ang)
        elbow=(base[0]+.53*dx,base[1]+.50*dy,base[2]+rng.uniform(-.04,.04))
        end=(base[0]+dx,base[1]+dy,base[2]+rng.uniform(.02,.13))
        limb(s,loc(base),loc(elbow),h*.016,h*.010);limb(s,loc(elbow),loc(end),h*.010,h*.003)
        for j in range(3):
            xx,yy=end[0]+rng.uniform(-.075,.075),end[1]+rng.uniform(-.08,.08)
            crown((xx,yy,end[2]+rng.uniform(-.027,.033)),rng.uniform(.084,.16),rng.uniform(.062,.12))
    crown(trunk[-1],.17,.13)


def footpath(s,top,coords,width):
    strip=[]
    for k,(a,b) in enumerate(zip(coords,coords[1:])):
        dx,dy=b[0]-a[0],b[1]-a[1];n=hypot(dx,dy);nx,ny=-dy/n,dx/n
        for i in range(10):
            t=i/10;x=a[0]+dx*t;y=a[1]+dy*t
            wid=width*(.87+.21*field(x*.75,y*.57,60))
            pair=[]
            for sign in (-1,1):
                xx,yy=x+wid*sign*nx,y+wid*sign*ny
                pair.append((xx,yy,top(xx,yy)+.22))
            strip.append(pair)
    for a,b in zip(strip,strip[1:]):
        s.face([a[0],b[0],b[1],a[1]],(170,150,107),1,.98)

def meadow(s,top,seed):
    rng=Random(seed)
    # Tufts, dry flower stems and exposed stones concentrate on broken ground.
    for i in range(350):
        x=rng.uniform(-14,14);y=rng.uniform(-7.4,7.4)
        if (x/15)**2+(y/8.6)**2>.78 or field(x*.38,y*.38,41)<.45:continue
        h=top(x,y)+.20; k=rng.uniform(.14,.36)
        for j in range(rng.randint(2,7)):
            xx=x+rng.gauss(0,.18);yy=y+rng.gauss(0,.14)
            wide=k*rng.uniform(.10,.34);height=k*rng.uniform(.61,1.16)
            col=rng.choice(((118,125,78),(161,158,92),(181,161,94),(100,118,81)))
            s.face([(xx-wide,yy,h),(xx+wide,yy,h),(xx+wide*.4,yy+.05,h+height)],col,2,1.12)
        if i%5==0:
            crag(s,x+.19,y+.21,h+.07,k*.92,k*.68,k*.39,seed+i)

def clockface(s,x,y,z,r,w):
    for axis in (0,1):
        for side in (-1,1):
            def pos(u,v,depth):
                return (x+u,y+side*(w*.445+depth),z+v) if axis==0 else (x+side*(w*.50+depth),y+u,z+v)
            points=[(r*cos(j*pi/20),r*sin(j*pi/20)) for j in range(40)]
            for scale,col,depth in ((1,'dressed',.08),(.88,'slate',.096),(.72,'iron',.11)):
                face=[pos(u*scale,v*scale,depth) for u,v in points]
                if (axis==0)==(side>0):face.reverse()
                s.face(face,col)
            for u,v in ((-.31*r,.37*r),(.40*r,.17*r)):
                s.face([pos(-.04*r,.02*r,.12),pos(.04*r,-.02*r,.12),pos(u,v,.12)],'brass',0,1.18)

def lanterns(s):
    b=s.board
    for x,y,z,scale in ((1.30,.91,2.2+11*.64,.37),(-4.8,1.83,4.55,.35),(3.76,2.52,3.96,.29),
                        (-7.68,.66,3.45,.22),(5.92,5.98,2.62,.22)):
        xx,yy,d=s.project((x,y,z))
        if not (0<xx<1 and 0<yy<1):continue
        idx=int(yy*b.height)*b.width+int(xx*b.width)
        if b.depth[idx]>d+.075:continue
        rad=s.view.scale*scale
        b.dab(xx,yy,rad*1.58,rad*.64,(182,121,49),.24,.17)
        b.dab(xx,yy,rad*.40,rad*.21,(240,183,84),.76,.16)
        b.dab(xx,yy,rad*.16,rad*.12,(250,212,128),.96,.07)

def swifts(b):
    for x,y,r in ((.23,.364,.049),(.312,.362,.032),(.325,.346,.023),(.418,.352,.014),(.434,.347,.011)):
        col=(84,76,76)
        coords=[(x-r*.54,y+r*.015),(x-r*.25,y-r*.041),(x-r*.08,y-r*.033),(x,y),
                (x+r*.27,y-r*.069),(x+r*.48,y-r*.071),(x+r*.30,y-r*.051),(x+.004*r,y+r*.027),(x-r*.23,y-r*.02)]
        b.polygon(coords,col,.88,.12)

def abbey(s):
    rx,ry,drop=16,8.7,20.8
    top=island(s,rx,ry,drop,431)
    footpath(s,top,[(-10.2,3.0),(-6.2,3.42),(-3.0,3.74),(-.17,2.15),(1.2,2.38),(3.1,3.4),(6.5,3.8),(9.4,2.1),(11.5,.6)],.26)
    z=2.20
    bridge(s,-14.1,7.5,4.42,11.4,4,1.13)
    # A steep detached abutment holds the western end of the viaduct.
    crag(s,-13.9,7.4,2.3,1.58,1.36,11.6,40)
    crag(s,-5.68,7.62,1.3,1.22,1.50,9,82)
    for x,y,rad in ((8.8,4.8,1.85),(8.95,6,1.1),(10,3,1.21),(-4.1,7.1,1.36),(-9.1,5.5,1.54)):
        crag(s,x,y,-1.7,rad,rad*.72,10+rad*2,int(30*x+38*y))
    box(s,-4.6,.25,1.1,6.7,5.3,1.56,'ruin')
    chapel(s,-4.05,.38,z+.45)
    dome(s,-6.50,-2.16,z+.55,1.80)
    # Terraced cliff dwellings rise directly out of the sunward face.
    for j in range(3):
        xx=3.3+1.25*j;yy=5.7-.23*j;base=.42+.32*j
        walls(s,xx,yy,base,1.88,1.51,2.05,windows=2)
        roof(s,xx,yy,base+2.05,2.04,1.66,.53,'tile',.25)
    tower(s,1.28,-.42,z,2.70,11.0)
    for x,y,w,d,h in ((4.65,1.24,2.45,2.5,2.74),(6.22,1.46,1.65,2.06,2.05),
                      (-8.14,-.48,2.1,2.23,1.82),(-9.9,1.35,1.7,1.65,1.62)):
        walls(s,x,y,z,w,d,h,windows=2)
        roof(s,x,y,z+h,w+.24,d+.27,.78,'tile',.33)
    # Coppiced avenue along the abbey approach; a few trees interrupt masonry edges.
    rng=Random(23)
    for x,y,h in ((-8.2,2.6,3.1),(-7.45,2.65,2.7),(-6.85,2.55,2.35),(-1.45,3.3,2.90),
                  (3.1,2.05,3.2),(3.55,2.20,3.35),(7.98,-.16,3.13),(8.6,-.45,2.27),(-8.3,-1.65,3.7)):
        tree(s,x,y,top(x,y)-.09,h,rng)
    vegetation(s,top,rx,ry,61,108)
    # The village walls turn and descend at the orchard. A narrow retaining wall traces the bluff.
    for j in range(10):
        x=7.3+j*.41; y=.62+.29*j; box(s,x,y,1.62,.59,.65,1.31-j*.058,'ruin')
    for i in range(3):
        x,y=(-10.5+i*2.1,-3.1-i*.14)
        box(s,x,y,top(x,y)-.5,1.25,.86,.96,'stone')
        roof(s,x,y,top(x,y)+.46,1.46,1.09,.49,'tile')

def foreground(s,seed,which):
    top=island(s,17,11,14,seed)
    rng=Random(78+which)
    footpath(s,top,[(-10,-5),(-7,-3),(-4,-2.7),(-1,-1.35),(2.5,-.65),(4.1,1.08),(8.01,2.08),(10.9,3.86)],.39)
    vegetation(s,top,17,11,seed+8,95,True)
    meadow(s,top,seed+21)
    if seed in (57,197):
        tx,ty=(7.38,-1.15) if seed==57 else (8.1,.65)
        pine(s,tx,ty,top(tx,ty),6.5 if seed==57 else 6.2,seed)
    elif seed==66: pine(s,-8.45,2.69,top(-8.45,2.69),6.8 if which==1 else 8.1,seed+which)
    # Two weathered masonry gateposts fix the viewer on the old departure path.
    if which in (0,2):
        x,y=(5.65,1.35) if which==0 else (-4.85,.75)
        z=top(x,y)-.38
        box(s,x,y,z,1.09,1.0,2.28,'ruin');box(s,x,y,z+2.28,1.30,1.14,.28,'dressed')
        for j in range(6):
            xx=x+(j+1)*.53;box(s,xx,y,z-.2,.55,.55,.95-j*.09,'ruin')
    for i in range(35):
        ang=rng.uniform(0,2*pi);r=rng.uniform(.8,7.2);x=r*cos(ang);y=r*sin(ang)
        if field(x*.45,y*.42,seed)<.5:continue
        tree(s,x,y,top(x,y)-.2,rng.uniform(.35,.74),rng,'silverleaf')

def skiff(board,x,y,w,direction=1):
    # Painted linen under tension, rigging and a bent prow. x/y are normalized panel coordinates.
    ph=board.phase
    hull=(78,66,50) if ph<2 else (56,55,56)
    red=((164,94,57),(159,80,54),(151,78,53),(97,79,77))[ph]
    flax=((224,197,145),(228,209,163),(223,170,113),(146,151,145))[ph]
    def pt(u,v):return (x+direction*w*u,y+w*v/3.5)
    def poly(coords,color,a=.98):board.polygon([pt(u,v) for u,v in coords],color,a,.05)
    def line(coords,color,sw,a=.91):board.stroke([pt(u,v) for u,v in coords],color,w*sw,a,.34)
    # A curved prow with stern cabin and slender keels, not a navigational icon.
    poly([(-.55,-.08),(-.39,-.01),(.23,-.042),(.55,-.16),(.43,-.016),(.28,.095),(-.15,.13),(-.37,.087)],hull)
    poly([(-.38,.037),(.31,-.007),(.48,-.102),(.33,.031),(-.13,.092)],mix(hull,flax,.39))
    poly([(-.34,-.065),(-.29,-.155),(-.14,-.15),(-.095,-.065)],hull)
    for mast,high,reach in ((.05,.97,.44),(-.28,.55,.23)):
        line([(mast,.01),(mast-.035,-high)],hull,.010)
        poly([(mast-.021,-high*.90),(mast+reach,-high*.34),(mast+reach*.86,-high*.25),
              (mast+reach*.47,-high*.235),(mast+.012,-high*.135)],flax if mast>0 else red)
        poly([(mast-.023,-high*.90),(mast+reach*.54,-high*.55),(mast+reach*.41,-high*.30),(mast+.008,-high*.14)],
             mix(flax if mast>0 else red,hull,.17),.72)
        for j in (1,2,3):
            t=j/4;line([(mast+.01+reach*t,-high*(.90-.57*t)),(mast+reach*.89*t,-high*(.145+.10*t))],mix(flax,hull,.4),.0023,.64)
        line([(mast-.032,-high*.95),(mast+reach*1.07,-high*.33)],hull,.006)
        line([(mast-.03,-high*.96),(-.49 if mast<0 else .50,-.05)],hull,.003)
    line([(.018,-.97),(.13,-1.01),(.20,-.985)],red,.009)
    if ph==3:
        board.dab(*pt(.25,-.06),w*.036,w*.036/3.5,(220,178,100),.62,.12)
        board.dab(*pt(.25,-.06),w*.014,w*.014/3.5,(250,218,134),.96,.06)

def stars(board):
    rng=Random(314)
    for i in range(215):
        x=rng.random();y=rng.uniform(.008,.49)
        if y>.26 and rng.random()>.32:continue
        if hypot(x-.73,(y-.235)*3.5)<.10:continue
        r=rng.uniform(.00055,.0014)*(1.38 if i%16==0 else 1)
        rgb=rng.choice(((185,195,184),(180,181,168),(207,184,151),(167,187,198)))
        board.dab(x,y,r,r/3.5,rgb,rng.uniform(.46,.81),.27)

VIEWS=(
    View(.70,.467,.0250,-.27,.145,9,.105),
    View(.39,.469,.0383,.32,.260,9,.050),
    View(.49,.474,.0301,-.99,.140,9,.090),
    View(.62,.493,.0284,.58,.140,9,.090),
)
def render(phase,width):
    board=OilCanvas(width,round(width*3.5),phase)
    # Rear islands each have a different plan, scale and amount of atmospheric separation.
    rear = (
        [(-.03,.332,.012,27,14),(.15,.557,.014,13,13),(.91,.59,.011,12,11)],
        [(.90,.345,.019,14,17),(.03,.565,.018,13,16),(.75,.604,.010,16,8)],
        [(.10,.347,.014,14,20),(.93,.55,.021,16,14),(.30,.596,.007,18,9)],
        [(.11,.361,.012,13,13),(.95,.386,.014,11,15),(.83,.598,.014,13,12)],
    )[phase]
    for i,(x,y,k,rx,drop) in enumerate(rear):
        s=Scene(board,View(x,y,k,-.43+i*.62,.17,3+i,.68-i*.06),73+i)
        top=island(s,rx,rx*.62,drop,179+i*123)
        if i==0:
            for j in range(3):
                xx=1.05*j-2; box(s,xx,0,top(xx,0),.83,.84,2.66+j*.36,'ruin')
    abbey_view=Scene(board,VIEWS[phase],431)
    abbey(abbey_view)
    # Discontinuous foreground frame, with either a sheltered hillside or its opposing bluff.
    front=(
        [(-.35,.87,.070,.43,57),(.98,1.07,.033,-.38,117)],
        [(1.31,.92,.069,-.42,66),(-.30,1.03,.045,.87,127)],
        [(-.39,.88,.075,.75,197),(1.16,1.10,.04,-.34,117)],
        [(1.23,.925,.070,-.65,66),(-.27,1.034,.048,.47,173)],
    )[phase]
    for i,(x,y,k,angle,seed) in enumerate(front):
        foreground(Scene(board,View(x,y,k,angle,.255,16+i, .10 if i else .065),seed),seed,phase)
    board.flush()
    board.lib.shadows(board.buffer,board.depth,board.width,board.height,phase)
    board.lib.crossing_clouds(board.buffer,board.depth,board.width,board.height,phase)
    boat=((.235,.499,.113,1),(.775,.592,.122,-1),(.19,.425,.081,1),(.27,.588,.106,1))[phase]
    skiff(board,*boat)
    if phase==2:swifts(board)
    if phase==3:lanterns(abbey_view)
    board.finish()
    if phase==3:stars(board)
    return Image.frombytes('RGB',(board.width,board.height),bytes(board.pixels))

def export_sidebar(master,phase,path):
    # The retained masters have their full paint values. On the work copy, darken mostly
    # the left label area and modulate the glaze by the existing brightness of the paint.
    image=master.resize((512,1792),Image.Resampling.LANCZOS)
    thumb=image.resize((64,224),Image.Resampling.BOX).convert('L')
    mask=Image.new('L',thumb.size)
    strength=[]
    for j in range(224):
        y=(j+.5)/224
        band=.16+.84*smooth((y-.335)/.14)*smooth((.765-y)/.13)
        for i in range(64):
            x=(i+.5)/64
            flank=.10+.90*smooth((.83-x)/.57)
            value=thumb.getpixel((i,j))/255
            header=.97*exp(-((y-.060)/.071)**2)*smooth((.68-x)/.35)
            strength.append(round(255*max(band*flank,header)*(.13+.49*value)))
    mask.putdata(strength)
    dark=Image.new('RGB',image.size,(33,37,40) if phase!='evening' else (45,37,39))
    image=Image.composite(dark,image,mask.resize(image.size,Image.Resampling.BICUBIC))
    image.save(path,quality=92,subsampling=0,optimize=True)

def main():
    ap=ArgumentParser(description=__doc__);ap.add_argument('phase',choices=(*PHASES,'all'))
    ap.add_argument('--width',type=int,default=960);ap.add_argument('--out',type=Path,default=HERE/'masters')
    ap.add_argument('--runtime',type=Path,help='also export opaque 512 × 1792 sidebar JPEGs')
    opt=ap.parse_args()
    if opt.width<96:ap.error('choose a width of at least 96')
    opt.out.mkdir(parents=True,exist_ok=True)
    if opt.runtime:opt.runtime.mkdir(parents=True,exist_ok=True)
    for phase in (PHASES if opt.phase=='all' else [opt.phase]):
        im=render(PHASES.index(phase),opt.width)
        im.save(opt.out/(phase+'.png'),compress_level=6)
        if opt.runtime:
            export_sidebar(im,phase,opt.runtime/(phase+'.jpg'))
        print(f'{phase}: {im.size}',flush=True)
if __name__=='__main__':
    main()
