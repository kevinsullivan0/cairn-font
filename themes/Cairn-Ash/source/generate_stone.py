from pathlib import Path
import random,math,struct,zlib,json
root=Path(__file__).resolve().parents[1]/'materials';root.mkdir(exist_ok=True)
n=512;r=random.Random(271828)
fields={k:[[r.random() for _ in range(k)] for _ in range(k)] for k in (4,8,16,64)}
def noise(x,y,k):
 cx,cy=(x%n)*k/n,(y%n)*k/n;ix,iy=int(cx),int(cy);fx,fy=cx%1,cy%1
 fx=fx*fx*(3-2*fx);fy=fy*fy*(3-2*fy)
 return sum(fields[k][(iy+dy)%k][(ix+dx)%k]*(fx if dx else 1-fx)*(fy if dy else 1-fy) for dx in (0,1) for dy in (0,1))
# Short branching fractures, rasterized with tapered pigment and periodic edges.
# There is no repeating horizontal seam or common slope across the tile.
fracture=[[0.0]*n for _ in range(n)]
def cut(x,y,xx,yy,strength):
 dx,dy=xx-x,yy-y;length2=dx*dx+dy*dy
 for py in range(math.floor(min(y,yy)-2),math.ceil(max(y,yy)+2)):
  for px in range(math.floor(min(x,xx)-2),math.ceil(max(x,xx)+2)):
   t=max(0,min(1,((px-x)*dx+(py-y)*dy)/length2))
   d=math.hypot(px-x-t*dx,py-y-t*dy)
   a=max(0,1-d/2.1)*strength
   fracture[py%n][px%n]=max(fracture[py%n][px%n],a)
for _ in range(4):
 x,y=r.uniform(0,n),r.uniform(0,n);angle=r.uniform(0,2*math.pi)
 for step in range(7):
  angle+=r.uniform(-.9,.9) if step in (2,5) else r.uniform(-.07,.07);length=r.uniform(18,38)
  xx,yy=x+length*math.cos(angle),y+length*math.sin(angle)
  strength=16*math.sin(math.pi*(step+.5)/7)*r.uniform(.55,1)
  cut(x,y,xx,yy,strength)
  if step==4:
   a=angle+r.choice((-1,1))*r.uniform(.65,1.2);l=r.uniform(12,25)
   cut(xx,yy,xx+l*math.cos(a),yy+l*math.sin(a),strength*.6)
  x,y=xx,yy
alphas=[];broad_values=[]
for y in range(n):
 row=[]
 for x in range(n):
  warp=(noise(x,y,8)-.5)*70
  broad=noise(x+warp,y-warp*.6,4);middle=noise(x,y,16);fine=noise(x,y,64);grit=r.random()
  broad_values.append(broad)
  a=round(3+30*broad+10*middle+4*fine+2*grit+fracture[y][x]+max(0,middle-.58)*18)
  if grit>.993:a+=9
  row.append(min(64,a))
 alphas.append(row)
def chunk(k,b):return struct.pack('>I',len(b))+k+b+struct.pack('>I',zlib.crc32(k+b)&0xffffffff)
mean_broad=sum(broad_values)/(n*n)
chrome=[[max(0,min(80,round(alphas[y][x]+14*(broad_values[y*n+x]-mean_broad)))) for x in range(n)] for y in range(n)]
for name,v,tile in [('basalt-grain',0,alphas),('limestone-grain',255,alphas),('basalt-chrome',0,chrome),('limestone-chrome',255,chrome)]:
 raw=b''.join(b'\0'+b''.join(bytes((v,v,v,a)) for a in row) for row in tile)
 png=b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
 (root/(name+'.png')).write_bytes(png)
(root/'texture.json').write_text(json.dumps({'tile_pixels':n,'seed':271828,'alpha_range':[min(map(min,alphas)),max(map(max,alphas))],'dark':'Black-only pigment, at most 64/255 opacity.','light':'White-only pigment, same opacity.','vein_opacity':0.045,'structure':'Warped mineral fields at three scales; sparse pits; four localized fractures with long planar runs, occasional angular turns, softened ends, and broad mineral patches. Periodic fields and wrapped fractures avoid tile-edge seams.','structural_variant':{'broad_amplitude_increase':14,'mean_centered':True,'alpha_cap':80,'scope':'Sidebars, ribbon and topbar only; same grit and fractures as the quiet tile.'},'scope':'Static mineral pigment on UI furniture. Note/editor/code reading surfaces excluded. Embedded assets; no network images or animated filters.'},indent=2)+'\n')
print('Built 512px mineral tiles: warped clouds, sparse pits, short branching fractures.')
