"""Build Cairn 1.0: four linked styles, desktop TTF and portable web WOFF.
Run from the packaged source directory, or with outputs on PYTHONPATH.
"""
from pathlib import Path
import argparse, math, json, hashlib
from shapely.geometry import Polygon, Point, LineString, MultiPoint, GeometryCollection, box
from shapely import affinity
from shapely.ops import unary_union
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont, newTable
from fontTools.agl import UV2AGL
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.svgLib.path import parse_path
from build_fonts import FlattenPen, geometry, to_glyph, polygons
import cairn, cairn_v, cairn_ii, cairn_iii, refine_relic

STYLES=[('Regular',400,False),('Italic',400,True),('Bold',700,False),('BoldItalic',700,True)]
SYMBOLS=set(range(0xA4,0xAA))|{0xAB,0xBB}
PATHS=dict(cairn_v.PATHS)
# A planed r crown and a broad cut on S echo the arch family at two scales.
PATHS.update({
 '(':["M 690 1500 L 460 1260 C 185 890 180 355 415 -20 L 620 -255"],
 ')':["M 160 1500 L 390 1260 C 665 890 670 355 435 -20 L 230 -255"],
 'r':[PATHS['r'][0],'M 205 705 L 435 1065 L 555 1050 L 690 900'],
 'S':['M 1070 1240 L 765 1450 L 585 1430 Q 300 1370 190 1130 Q 145 935 435 765 L 820 535 Q 1200 220 780 100 C 505 5 295 80 120 330'],
 '+':['M 160 665 L 1000 665','M 580 1085 L 580 245'],
 '<':['M 830 1150 L 180 650 L 830 150'],
 '>':['M 180 1150 L 830 650 L 180 150'],
 '[':['M 620 1490 L 230 1490 L 230 -230 L 620 -230'],
 ']':['M 170 1490 L 560 1490 L 560 -230 L 170 -230'],
 '{':['M 720 1490 L 490 1470 Q 295 1400 360 1040 Q 410 775 170 630 Q 410 485 360 220 Q 295 -140 490 -210 L 720 -230'],
 '}':['M 170 1490 L 400 1470 Q 595 1400 530 1040 Q 480 775 720 630 Q 480 485 530 220 Q 595 -140 400 -210 L 170 -230'],
 '^':['M 160 990 L 490 1420 L 820 990'],
 '_':['M 100 -200 L 1050 -200'],
 '`':['M 170 1490 L 400 1210'],
 '|':['M 270 1490 L 270 -230'],
 '~':['M 125 615 Q 335 880 565 665 Q 795 450 1005 715'],
 '¤':['M 270 420 L 270 980 L 830 980 L 830 420 Z','M 150 300 L 350 500','M 750 900 L 950 1100','M 150 1100 L 350 900','M 750 500 L 950 300'],
 '¥':['M 130 1420 L 650 735 L 1225 1420','M 650 735 L 615 65','M 300 650 L 970 650','M 300 390 L 970 390'],
 '¦':['M 270 1490 L 270 850','M 270 410 L 270 -230'],
 '§':['M 770 1330 Q 400 1580 235 1290 Q 105 1080 475 880 L 700 735 Q 1010 500 730 310 Q 500 165 250 360',
      'M 250 1070 Q -35 820 260 615 L 560 420 Q 975 175 700 -65 Q 475 -220 165 15'],
 '«':['M 480 1050 L 170 650 L 480 250','M 950 1050 L 640 650 L 950 250'],
 '»':['M 170 1050 L 480 650 L 170 250','M 640 1050 L 950 650 L 640 250'],
 '–':['M 110 650 L 1000 650'],
 '—':['M 110 650 L 1750 650'],
 '−':['M 160 665 L 1000 665'],
 '‘':['M 270 1490 L 170 1350 L 255 1180'],
 '’':['M 190 1490 L 290 1350 L 205 1180'],
 '@':['M 1100 225 Q 745 -120 345 105 C -125 370 -25 1160 385 1395 Q 860 1640 1220 1250 C 1510 875 1240 290 990 455 L 1015 1030',
      'M 1000 910 Q 805 1160 565 975 C 345 795 370 415 625 400 Q 865 395 990 690'],
})
ADDITIONS={ord(ch):f'uni{ord(ch):04X}' for ch in '+<>@[]^_`{|}~–—−‘’…•\u00a0'}


def draw(ch,bold=False,italic=False):
    paths=dict(PATHS)
    if italic:
        # Purpose-drawn cursive construction, with firm feet and no swash.
        paths.update({
          'a':[cairn.LEFT,'M 865 1080 L 830 240 L 900 65 L 1050 140'],
          'f':['M 130 -350 L 285 -160 L 315 655 L 270 1090 Q 280 1450 500 1490 L 680 1340',PATHS['f'][1]],
          'l':['M 240 1515 L 205 240 L 325 75 L 535 170'],
          'y':['M 110 1070 L 505 85','M 995 1070 L 605 200 L 425 -135 L 215 -335 L 55 -300'],
        })
    if bold:
        # Open e's eye and move the lower exit away from its crossbar.
        paths['e']=['M 145 440 L 915 700 L 840 930 L 615 1100 C 270 1100 90 815 145 480 C 200 175 410 20 665 100 L 925 220']
        paths['c']=['M 875 910 L 640 1080 C 280 1135 95 860 140 525 C 175 205 390 25 640 95 L 900 225']
    contours=[]
    for svg in paths.get(ch,[]):
        pen=FlattenPen(step=7);parse_path(svg,pen);contours.extend(pen.contours)
    lines=[LineString(p) for p in contours]
    def stroke(points,weight):
        ends=(True,True)
        if points in contours:
            index=contours.index(points)
            if index:
                ends=tuple(not any(i!=index and line.distance(Point(p))<95 for i,line in enumerate(lines)) for p in (points[0],points[-1]))
        rx,ry=(167,73) if bold else (135,53)
        angle=math.radians(-22)
        face=[(-rx,0),(-rx*.42,-ry),(rx*.70,-ry*.55),(rx,0),(rx*.42,ry),(-rx*.70,ry*.55)]
        nib=[(weight*.98*(x*math.cos(angle)-y*math.sin(angle)),weight*.98*(x*math.sin(angle)+y*math.cos(angle))) for x,y in face]
        head=[(x*(1.05 if bold else 1),y) for x,y in cairn_v.HEAD]
        return cairn_ii.stroke(points,weight,blade=ch in 'cersCGS',nib=nib,blade_length=110,blade_width=63 if bold else 52,head=head,terminal_ends=ends)
    g=cairn.draw(ch,paths=paths,stroke_fn=stroke,dot_y=1465 if bold else 1450,
        dot_scale=(1.52 if bold else 1.4) if ch in 'ij' else (1.28 if bold else 1.08))
    if ch in '‘’“”„':
        # Quote marks need a legible comma silhouette, without stem serifs.
        mark=Polygon([(70,85),(180,155),(270,85),(235,-60),(125,-190),(165,-40),(85,-20)])
        if bold:mark=affinity.scale(mark,xfact=1.12,yfact=1.07,origin=(170,0))
        if ch in '‘“':mark=affinity.rotate(mark,180,origin=(170,0))
        mark=affinity.translate(mark,yoff=1280 if ch!='„' else 105)
        g=unary_union([mark,affinity.translate(mark,xoff=415)]) if ch in '“”„' else mark
    if ch=='•':g=Polygon([(80,650),(230,795),(375,650),(230,505)])
    if ch=='¨':
        g=unary_union([affinity.translate(draw('.',bold,False),xoff=x,yoff=1300) for x in (0,420)])
    if ch=='©':
        ring=Point(710,710).buffer(660,quad_segs=48).difference(Point(710,710).buffer(565 if not bold else 540,quad_segs=48))
        letter=affinity.scale(draw('C',bold,False),xfact=.58,yfact=.58,origin=(0,0))
        x0,y0,x1,y1=letter.bounds
        letter=affinity.translate(letter,xoff=710-(x0+x1)/2,yoff=710-(y0+y1)/2)
        g=unary_union([ring,letter])
    if ch=='…':
        d=draw('.',bold,False)
        g=unary_union([affinity.translate(d,xoff=x) for x in [0,455,910]])
    if ch in 'hnm':
        for offset in ([0,560] if ch=='m' else [0]):
            cut=Polygon([(350+offset,800),(475+offset,700),(545+offset,900)])
            g=g.difference(affinity.skew(cut,1,0,origin=(0,0)))
    g=unary_union([Polygon(p.exterior,[r for r in p.interiors if Polygon(r).area>=2000]) for p in polygons(g)])
    if bold:g=affinity.scale(g,xfact=1.045,origin=(0,0))
    if italic:
        g=affinity.scale(g,xfact=.97,origin=(0,0))
        g=affinity.skew(g,8,0,origin=(0,0))
    return g.simplify(.65,preserve_topology=True)


def spacing(geos,metrics,cmap,bold):
    chars=''.join(chr(cp) for cp in sorted(cmap) if cp < 0xE000 and cp not in {32,160,168})
    pairs,report=refine_relic.optical_kerning(geos,metrics,cmap,
        lower_target=275 if bold else 265,other_target=235 if bold else 225,punct_target=180,
        minimum_gap=140,maximum_positive=220,chars=chars,enforce_all_pairs=True,lower_limit=-240,other_limit=-480)
    for a in chars:
        if not a.isalnum():continue
        na=cmap[ord(a)]
        for b in '.,:;…':
            nb=cmap[ord(b)];pair=(na,nb);change=pairs.get(pair,0)
            while change>-480:
                candidate=affinity.translate(geos[nb],xoff=metrics[na][0]+change-5)
                if geos[na].distance(candidate)<140:break
                change-=5
            if change:pairs[pair]=change
            else:pairs.pop(pair,None)
    report['pair_count']=len(pairs)
    return pairs,report


def build(root,styles):
    (root/'desktop').mkdir(parents=True,exist_ok=True);(root/'web/fonts').mkdir(parents=True,exist_ok=True)
    repertoire=set(range(32,127))|SYMBOLS|set(ADDITIONS)|{0x201C,0x201D,0x201E}
    cmap={cp:UV2AGL.get(cp,f'uni{cp:04X}') for cp in sorted(repertoire)}
    order=['.notdef','.null','nonmarkingreturn']+list(dict.fromkeys(cmap.values()))
    reverse={v:chr(k) for k,v in cmap.items()}
    reports=[]
    for key,weight,italic in STYLES:
        if key not in styles:continue
        bold=weight==700;glyphs={};metrics={};geos={}
        for name in order:
            ch=reverse.get(name,'')
            if name=='.notdef':
                g=box(100,0,900,1400).difference(box(220,120,780,1280))
            elif ch in ' \u00a0' and ch:
                g=GeometryCollection()
            else:
                g=draw(ch,bold,italic) if ch else GeometryCollection()
                assert not ch or not g.is_empty,('Missing independently drawn glyph',ch)
            if g.is_empty:
                glyphs[name]=to_glyph(g);metrics[name]=(590 if bold else 560,0);continue
            if ch.isdigit():
                _,y0,_,y1=g.bounds;g=affinity.translate(g,yoff=-y0);g=affinity.scale(g,yfact=1390/(y1-y0),origin=(0,0))
            left,right=cairn_iii.bearings(ch)
            x0,y0,x1,y1=g.bounds;g=affinity.translate(g,xoff=left-x0)
            glyphs[name]=to_glyph(g);metrics[name]=(math.ceil(x1-x0+left+right),left);geos[name]=g
        pairs,report=spacing(geos,metrics,cmap,bold)
        # True tabular figures are alternate glyphs, leaving prose figures proportional.
        font_order=list(order)
        tabwidth=max(metrics[cmap[ord(ch)]][0] for ch in '0123456789')+30
        for ch in '0123456789':
            source_name=cmap[ord(ch)];name=source_name+'.tnum';g=geos[source_name]
            x0,_,x1,_=g.bounds;g=affinity.translate(g,xoff=(tabwidth-(x1-x0))/2-x0)
            glyphs[name]=to_glyph(g);metrics[name]=(tabwidth,round(g.bounds[0]));font_order.append(name)
        style='Bold Italic' if key=='BoldItalic' else key
        fb=FontBuilder(2048,isTTF=True);fb.setupGlyphOrder(font_order);fb.setupCharacterMap(cmap);fb.setupGlyf(glyphs)
        fb.setupHorizontalMetrics(metrics)
        fb.setupHorizontalHeader(ascent=1800,descent=-600,lineGap=80,caretSlopeRise=1000,caretSlopeRun=158 if italic else 0)
        fb.setupNameTable({'familyName':'Cairn','styleName':style,'typographicFamily':'Cairn','typographicSubfamily':style,
            'uniqueFontIdentifier':f'Cairn 1.001 {style} personal edition','fullName':f'Cairn {style}',
            'psName':f'Cairn-{key}','version':'Version 1.001',
            'copyright':'Cairn design project, 2026. All included glyphs drawn for this project.',
            'description':'Carved, proportional type for prose. Personal edition derived from the Cairn V study.',
            'licenseDescription':'No distribution license specified. All included glyphs are generated from the included drawing source.'})
        selection=(0x20 if bold else 0)|(0x1 if italic else 0)|(0x40 if not bold and not italic else 0)|0x80
        fb.setupOS2(version=4,sTypoAscender=1800,sTypoDescender=-600,sTypoLineGap=80,
            usWinAscent=1900,usWinDescent=650,sxHeight=1110,sCapHeight=1510,usWeightClass=weight,usWidthClass=5,
            fsSelection=selection,fsType=0,yStrikeoutSize=90,yStrikeoutPosition=570)
        fb.setupPost(italicAngle=-9 if italic else 0,isFixedPitch=0,underlinePosition=-230,underlineThickness=85)
        fb.setupMaxp();fb.font['head'].macStyle=(1 if bold else 0)|(2 if italic else 0)
        # Fixed build timestamp makes identical source builds reproducible.
        fb.font.recalcTimestamp=False;fb.font['head'].created=fb.font['head'].modified=3875904000
        gasp=newTable('gasp');gasp.gaspRange={65535:0x000A};fb.font['gasp']=gasp
        feature='languagesystem DFLT dflt; languagesystem latn dflt; feature kern {\n'
        feature+='\n'.join(f'pos {a} {b} {value};' for (a,b),value in sorted(pairs.items()))+'\n} kern;'
        feature+='feature tnum {\n'+''.join(f'sub {cmap[ord(ch)]} by {cmap[ord(ch)]}.tnum;\n' for ch in '0123456789')+'} tnum;'
        addOpenTypeFeaturesFromString(fb.font,feature)
        path=root/'desktop'/f'Cairn-{key}.ttf';fb.save(path)
        webfont=TTFont(path,recalcTimestamp=False);webfont.flavor='woff';webfont.save(root/'web/fonts'/f'Cairn-{key}.woff')
        report.update(style=style,characters=len(cmap),glyphs=len(font_order),file=path.name,sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        reports.append(report);print(json.dumps(report),flush=True)
    (root/'build-report.json').write_text(json.dumps(reports,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent.parent)
    p.add_argument('--styles',nargs='+',default=[s[0] for s in STYLES]);a=p.parse_args();build(a.output,a.styles)
