// Native pigment fields, triangular depth spans and directional hog-bristle marks
// for raster.Canvas. Coordinates for weather and brush marks are in panel widths.
#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <vector>
using std::min; using std::max;
struct C {double r,g,b; C operator+(C q)const{return {r+q.r,g+q.g,b+q.b};} C operator-(C q)const{return {r-q.r,g-q.g,b-q.b};} C operator*(double f)const{return {r*f,g*f,b*f};}};
static C mix(C a,C b,double k){return a+(b-a)*k;}
static double sat(double x){return min(1.,max(0.,x));}
static double ease(double lo,double hi,double x){x=sat((x-lo)/(hi-lo));return x*x*(3-2*x);}
static uint32_t hash(uint32_t n){n^=n>>16;n*=0x7feb352d;n^=n>>15;n*=0x846ca68b;return n^(n>>16);}
static double rnd(int x,int y,int z){return hash(uint32_t(x)*0x9e3779b9u+uint32_t(y)*0x85ebca6bu+uint32_t(z)*0xc2b2ae35u)*(1./4294967296.);}
static double noise(double x,double y,int s){
 int i=floor(x),j=floor(y);x-=i;y-=j;x=x*x*(3-2*x);y=y*y*(3-2*y);
 double a=rnd(i,j,s),b=rnd(i+1,j,s),c=rnd(i,j+1,s),d=rnd(i+1,j+1,s);
 return a+(b-a)*x+(c-a)*y+(a-b-c+d)*x*y;
}
static double fb(double x,double y,int s){
 double q=0,amp=.53;for(int j=0;j<5;j++){q+=amp*(2*noise(x,y,s+j*7)-1);double u=1.66*x+1.18*y+.49;y=-1.18*x+1.66*y+.91;x=u;amp*=.49;}return q;
}
static double sq(double x){return x*x;}
struct State{C zen,lit,hor,cloud,high,valley,far,rock,snow;double sunx,suny,slant;};
static const State states[]={
 {{74,113,131},{181,179,152},{237,197,142},{111,122,134},{250,224,175},{88,111,110},{165,160,143},{109,129,129},{227,212,178},.78,.39,-1},
 {{48,98,130},{137,174,181},{205,206,171},{106,139,154},{249,237,204},{66,98,99},{150,168,160},{90,124,134},{231,231,210},.15,.19,1},
 {{58,81,107},{173,134,127},{249,161,102},{102,94,112},{249,175,117},{76,78,94},{168,132,128},{105,96,117},{235,165,133},.13,.52,1},
 {{22,32,54},{58,83,99},{115,139,146},{57,69,89},{151,174,174},{33,51,65},{83,111,123},{63,84,105},{157,178,183},.73,.235,-1}};
static C get(unsigned char*p,int i){return {double(p[3*i]),double(p[3*i+1]),double(p[3*i+2])};}
static void put(unsigned char*p,int i,C c){p[3*i]=max(0.,min(255.,c.r))+.49;p[3*i+1]=max(0.,min(255.,c.g))+.49;p[3*i+2]=max(0.,min(255.,c.b))+.49;}
static double clouds(double x,double v,int phase,int s){
 double y=v*3.5;
 // Anvil and cumulus banks separated by openings; their scale varies with altitude.
 double profile=-.19+.12*sin(2.4*x+4.8*y+phase)+.13*cos(6.8*y+phase*.9);
 double cloud=fb(x*1.55+y*.45,y*3.05,s+2);
 double drift=noise(x*1.8,y*2.,17+s);
 return cloud*.70+fb(3.5*x+.85*drift,6.5*y-.91*drift,s+41)*.29+profile;
}
static double mountain(double x,int k,int t){
 // Three broken alpine ridges, each with individual peaks and asymmetric spurs.
 double base=.681+.073*k;
 double crest=0;
 static const double xpos[][6]={{-.16,.18,.42,.74,1.09,1.3},{-.13,.17,.52,.73,1.02,1.32},{-.14,.19,.38,.69,1.04,1.24}};
 static const double ht[][6]={{.070,.056,.080,.065,.10,.08},{.126,.071,.083,.121,.088,.13},{.148,.129,.093,.117,.153,.10}};
 for(int j=0;j<6;j++){double dx=x-(xpos[k][j]+.062*sin(.9*t+k+j)); double h=ht[k][j]*(1+.16*sin(1.7*t+j));
 crest=max(crest,h-std::abs(dx)*(dx<0?.28+.09*noise(j,k,3):.25+.12*noise(k,j,1)));}
 return base-crest+.021*fb(5.2*x,1.3*k+2*t,83)+.008*fb(21*x,6+k,23)+.003*fb(70*x,k,49);
}
extern "C" void atmosphere(unsigned char*p,int w,int h,int phase) {
 auto a=states[phase];int seed=91+phase*7;
 std::vector<std::array<double,3>> ridges(w);for(int i=0;i<w;i++)for(int k=0;k<3;k++)ridges[i][k]=mountain((i+.5)/w,k,phase);
 for(int j=0;j<h;j++)for(int i=0;i<w;i++){
 double x=(i+.5)/w,v=(j+.5)/h;
 C c=mix(a.zen,a.hor,ease(-.04,.63,v));c=mix(c,a.lit,.28*std::exp(-sq((v-.30)/.25)));
 double light=std::exp(-2.5*(sq(x-a.sunx)+sq((v-a.suny)*3.5)));
 c=mix(c,a.high,light*(phase==3?.24:.42));
 double b=clouds(x,v,phase,seed);
 if(v<.70 && b>-.13){
 double prox=clouds(x+.030*a.slant,v-.014,phase,seed);
 double silver=sat(.43+1.95*(b-prox)+.43*light+.08*fb(x*12,v*37,seed));
 C paint=mix(a.cloud,a.high,silver); double alpha=ease(-.115,.19,b)*(.78+.16*light);
 c=mix(c,paint,alpha*(1-ease(.52,.71,v)));
 }
 if(phase==3){
 double dx=x-a.sunx,dy=(v-a.suny)*3.5,dist=sqrt(dx*dx+dy*dy);
 if(dist<.063){double xx=dx/.062,yy=dy/.062,zz=sqrt(max(0.,1-xx*xx-yy*yy));
 double sun=sat((-xx*.71-.25*yy+.18*zz)*2.7);
 C moon=mix({85,104,119},{219,222,197},sun*(.90+.11*fb(52*x,172*v,876)));
 c=mix(c,moon,ease(.063,.060,dist)*(1-.75*ease(-.1,.13,b)));}}
 else if(phase==2 || phase==0){
 double rad=phase==2?.031:.028,ds=sqrt(sq(x-a.sunx)+sq((v-a.suny)*3.5));
 if(ds<rad+.012)c=mix(c,{255,225,161},ease(rad+.003,rad-.002,ds)*(.85-.65*ease(-.1,.13,b)));
 }
 for(int k=0;k<3;k++){
 double top=ridges[i][k], below=(v-top)*3.5;if(below<0)continue;
 double f=fb(5*x+2.2*below,5.7*below+.6*k,27+phase);
 double flutes=fb(18*x+4.5*below+f*.45,3.7*below,27+k);
 double facet=sat(.50+1.15*f+.75*flutes);
 C stone=mix(a.rock,a.valley,.24+.48*ease(0,.38,below));
 stone=mix(stone,a.snow,ease(.10,.79,facet)*ease(.52,-.10,below+f*.12)*(.87-.14*k));
 double mist=.64-.18*k+.11*std::exp(-sq((below-.26)/.12));
 c=mix(stone,a.far,mist);
 }
 // Mist threads across low valleys, following wind-sheared openings.
 if(v>.63){double mist=ease(.63,.76,v)*ease(1.13,.83,v)*ease(.0,.4,fb(x*1.9+v*3,v*29,391+phase));c=mix(c,a.hor,mist*.47);}
 put(p,j*w+i,c);
 }
}

// Banks of vapour on either side of the viewing path, painted after the geology. A union of
// irregular billows gives each bank an upper sunlit rim, broad half-tone and an evaporating base.
struct Bank {double x,y,r,ht;};
static const Bank courses[][3]={
 {{-.09,.16,.86,.071},{1.12,.630,.75,.037},{-.24,.748,.75,.055}},
 {{1.06,.187,.91,.101},{-.16,.644,.65,.052},{1.01,.708,.69,.045}},
 {{.98,.249,.79,.060},{-.21,.638,.94,.040},{.99,.760,.82,.041}},
 {{-.12,.156,.81,.048},{1.12,.614,.84,.050},{-.10,.721,.73,.047}}};
static double body(double x,double y,const Bank& b,int seed){
 double xx=(x-b.x)/b.r, yy=(y-b.y)/b.ht;
 double wx=xx+.09*fb(5*x,13*y,seed);
 double best=-9.;
 for(int i=0;i<8;i++){double off=(i-3.5)*.217;
 double rr=.22+.17*rnd(i,4,seed),lift=.08+.44*rnd(i,9,seed);
 double h=.48+.47*rnd(i,12,seed);
 double d=1-sq((wx-off)/rr)-sq((yy+lift)/h);best=max(best,d);}
 double fray=fb(5.5*x+1.2*y,24*y,seed+1)*.6+fb(18*x,60*y,seed+14)*.30;
 return best*.6+fray;
}
extern "C" void crossing_clouds(unsigned char*p,float*depth,int w,int h,int phase){
 State a=states[phase];
 for(int n=0;n<3;n++){
 auto b=courses[phase][n];int seed=391+phase*9+n*7;
 for(int j=max(0,int((b.y-1.68*b.ht)*h));j<min(h,int((b.y+1.23*b.ht)*h));j++)for(int i=0;i<w;i++){
 int idx=j*w+i;double x=(i+.5)/w,y=(j+.5)/h,xx=(x-b.x)/b.r;if(std::abs(xx)>1.30||depth[idx]>14)continue;
 double d=body(x,y,b,seed);if(d<-.40)continue;
 double light=sat(.52+(d-body(x+a.slant*.012,y-.013,b,seed))*.53
                       -.19*(y-b.y)/b.ht+.20*fb(x*9,y*31,seed+7));
 C cloud=mix(a.cloud,a.high,light);
 double amp=n==0?.78:n==1?.65:.55;
 double opacity=ease(-.39,.44,d)*amp;
 if(depth[idx]>6)opacity*=.85;
 put(p,idx,mix(get(p,idx),cloud,opacity));
 }}}

// Each vertex is screen x,y,view depth,u,v; RGB and material finish follow the triangle.
extern "C" void spans(unsigned char*p,float *depth,int w,int h,const float*data,int count) {
 for(int n=0;n<count;n++,data+=20){
 const float *a=data,*b=a+5,*c=b+5; double x0=a[0]*w,y0=a[1]*h,x1=b[0]*w,y1=b[1]*h,x2=c[0]*w,y2=c[1]*h;
 double det=(x1-x0)*(y2-y0)-(y1-y0)*(x2-x0);if(std::abs(det)<.001)continue;
 int lx=max(0,(int)floor(min({x0,x1,x2}))),rx=min(w-1,(int)ceil(max({x0,x1,x2})));
 int ly=max(0,(int)floor(min({y0,y1,y2}))),ry=min(h-1,(int)ceil(max({y0,y1,y2})));
 int material=int(data[18]);double seed=data[19];C color={data[15],data[16],data[17]};
 for(int y=ly;y<=ry;y++)for(int x=lx;x<=rx;x++){
 double u=((x+.5-x0)*(y2-y0)-(y+.5-y0)*(x2-x0))/det;
 double v=((y+.5-y0)*(x1-x0)-(x+.5-x0)*(y1-y0))/det; double t=1-u-v;
 if(min({u,v,t})<-.00002)continue; int idx=y*w+x;double z=t*a[2]+u*b[2]+v*c[2];if(z<depth[idx])continue;depth[idx]=z;
 double X=t*a[3]+u*b[3]+v*c[3],Y=t*a[4]+u*b[4]+v*c[4],variation=0,hue=0;
 if(material==1){ // Fractured rock: differential erosion, occasional bedding planes, mineral sweeps.
 double br=fb(X*.21+Y*.041,Y*.23,113+seed);double fault=fb(X*.68+br*1.9,Y*.24,57+seed);
 double lam=sin(Y*4+X*.56+6*br+1.3*fault);double breakline=fb(X*.16+br,Y*.77,107+seed);
 double stain=fb(X*.21+Y*.18+br*1.2,Y*.47,132+seed);
 variation=br*.33+fault*.24+stain*.20+ease(.70,.94,lam)*.075-.085*ease(.23,-.02,std::abs(breakline));

 hue=fb(X*.35,Y*.41,111+seed)*16;
 }else if(material==2){ // Hillside turf and shrubs.
 double th=fb(X*.42,Y*.6,47+seed);variation=th*.34+.115*fb(X*1.7,Y*2.3,39+seed);hue=th*16;
 }else if(material==3){ // Irregular ashlar, with muted joints and lime wash.
 double row=floor(Y*2.05+.035*noise(X*4,Y,41)), course=Y*2.05-floor(Y*2.05);
 double block=X*1.18+noise(row,seed,11)*3.4+.1*noise(X,Y,12);
 variation=(noise(floor(block),row,seed+75)-.5)*.13-.145*ease(.86,.99,course)-.13*ease(.86,.99,block-floor(block))+.16*fb(X*.57,Y*.42,148)+.095*fb(X*1.25,Y*1.4,146);
 }else if(material==4){double tile=X*3.4+.1*fb(X,Y,43);
 variation=.19*fb(X*.9,Y*.7,17)+.065*sin(tile*6.283)+.085*fb(X*3.4,Y*.8,38);
 }
 put(p,idx,color*(1+variation)+C{hue,.18*hue,-hue*.65});
 }}}

// Trace towards the painted sun in the view's depth buffer. Nearby projecting eaves,
// trees and arcades cast shadows over their own ground plane and adjacent masonry.
extern "C" void shadows(unsigned char*p,const float*depth,int w,int h,int phase){
 const double lx[]={-.85,.66,-.92,.68},ld[]={.40,-.17,-.18,-.42},lz[]={.51,.80,.34,.63};
 const double tilts[]={.145,.26,.14,.14};
 for(int j=0;j<h;j++)for(int i=0;i<w;i++){
 int id=j*w+i;double base=depth[id];if(base<1)continue;
 double angle=base>13?.255:tilts[phase];
 double vy=ld[phase]*sin(angle)-lz[phase]*cos(angle),vz=ld[phase]*cos(angle)+lz[phase]*sin(angle);
 double shade=0;for(double travel=2.5/w;travel<.245;travel=travel*1.21+1./w){
 int x=round(i+w*travel*lx[phase]),y=round(j+w*travel*vy);if(x<0||x>=w||y<0||y>=h)break;
 double delta=depth[y*w+x]-base-vz*travel;
 if(delta>.004+travel*.042 && delta<.64 && std::abs(depth[y*w+x]-base)<.8){
 double k=ease(.004+travel*.044,.012+travel*.085,delta)*(1-.40*travel/.245);shade=max(shade,k);
 }}
 if(shade>.005){C c=get(p,id);double haze=base<7?.60:1.;
 double k=shade*haze*(phase==3?.68:1.);
 put(p,id,{c.r*(1-.28*k),c.g*(1-.215*k),c.b*(1-.135*k)});}
 }}

struct Rng { uint32_t s; uint32_t raw(){s=s*1664525u+1013904223u;return s;} double any(){return raw()/4294967296.;}};
static double lum(C a){return .27*a.r+.54*a.g+.19*a.b;}
static double dist(C a,C b){C d=a-b;return sqrt(.34*d.r*d.r+.48*d.g*d.g+.18*d.b*d.b);}
struct Integral{
 int w,h;std::vector<std::array<uint32_t,3>> a;
 Integral(unsigned char*p,int W,int H):w(W),h(H),a((w+1)*(h+1)){
 for(int y=1;y<=h;y++){uint32_t q[3]={};for(int x=1;x<=w;x++){for(int k=0;k<3;k++){q[k]+=p[3*((y-1)*w+x-1)+k];a[y*(w+1)+x][k]=a[(y-1)*(w+1)+x][k]+q[k];}}}}
 C avg(int x,int y,int radius)const{
 int x0=max(0,x-radius),x1=min(w,x+radius+1),y0=max(0,y-radius),y1=min(h,y+radius+1);
 double s=1./((x1-x0)*(y1-y0));double rgb[3];for(int k=0;k<3;k++)rgb[k]=(a[y1*(w+1)+x1][k]-a[y1*(w+1)+x0][k]-a[y0*(w+1)+x1][k]+a[y0*(w+1)+x0][k])*s;
 return {rgb[0],rgb[1],rgb[2]};
 }};
extern "C" void paint(unsigned char* p,int w,int h,int seed){
 Integral src(p,w,h);Rng rng{uint32_t(seed+241)};
 // Lose the hard geometric underdrawing first. Build the marks broad-to-fine, reserving
 // shorter bristles for the silhouettes where the gesture would cross a strong edge.
 for(int y=0;y<h;y++)for(int x=0;x<w;x++)put(p,y*w+x,src.avg(x,y,max(2,w/93)));
 for(double size:{.024,.0110,.0048,.0020}){
 double rad=max(1.05,size*w);int step=max(2,int(rad*1.05)),sample=max(1,int(rad*.44));
 std::vector<std::array<int,2>> sites;for(int y=0;y<h;y+=step)for(int x=0;x<w;x+=step)sites.push_back({min(w-1,x+int(rng.any()*step)),min(h-1,y+int(rng.any()*step))});
 for(size_t j=sites.size();j>1;j--)std::swap(sites[j-1],sites[rng.raw()%j]);
 for(auto xy:sites){
 int x=xy[0],y=xy[1];C ref=src.avg(x,y,sample),base=get(p,y*w+x);
 double delta=dist(ref,base);
 if(size<.008 && delta<(size<.003?4.8:6.4) && rng.any()>.11)continue;
 int diff=max(2,int(rad));double dx=lum(src.avg(min(w-1,x+diff),y,sample))-lum(src.avg(max(0,x-diff),y,sample));
 double dy=lum(src.avg(x,min(h-1,y+diff),sample))-lum(src.avg(x,max(0,y-diff),sample));double grad=hypot(dx,dy);
 double field=fb(4.*x/w,4.*y/w,seed)*1.55-.11;
 double ang=grad>3?atan2(dx,-dy):field;ang+=(rng.any()-.5)*(.45+.6/(1+grad*.12));
 double cs=cos(ang),sn=sin(ang),len=rad*(1.22+rng.any()*1.55),wide=rad*(.33+.37*rng.any());
 double bend=(rng.any()-.5)*.72,bristle=rng.any()*6,load=.64+.29*rng.any();
 double tint=(rng.any()-.5)*(size>.008?14:9),val=(rng.any()-.5)*(size>.008?13:6);
 C pigment=ref+C{val+tint*.6,val+tint*.04,val-tint*.62};
 int hw=ceil(std::abs(cs)*len+std::abs(sn)*wide*1.6+2),hh=ceil(std::abs(sn)*len+std::abs(cs)*wide*1.6+2);
 for(int j=max(0,y-hh);j<=min(h-1,y+hh);j++)for(int i=max(0,x-hw);i<=min(w-1,x+hw);i++){
 double u=((i-x)*cs+(j-y)*sn)/len;if(std::abs(u)>=1)continue;
 double v=(-(i-x)*sn+(j-y)*cs)/wide-bend*(u*u-.28);
 double edge=1-v*v/std::max(.01,1-u*u); if(edge<=0)continue;
 double k=sat(edge*3.)*load;double fil=sin((v*wide*.97)+bristle+u*.83)+.45*sin(v*wide*2.35+bristle);
 int ind=j*w+i;C under=get(p,ind);put(p,ind,mix(under,pigment+C{1.,.87,.71}*(fil*2.3),k*(.92+.055*fil)));
 }
 }}
 // Pigment caught in fine linen. Texture amplitude is intentionally below the brush modulation.
 for(int y=0;y<h;y++)for(int x=0;x<w;x++){auto c=get(p,y*w+x);double g=(rnd(x,y,seed)-.5)*3.4+.7*sin(x*2.16+.42*sin(y*.21))+.4*sin(y*2.03);put(p,y*w+x,c+C{g,g*.96,g*.83});}
}
