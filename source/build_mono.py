"""Cairn Mono: fixed cells, refitted stroke skeletons, four linked styles.
Run beside build_family.py. No original/reference fonts are needed.
"""
from pathlib import Path
import argparse, json, math, hashlib
from shapely import affinity
from shapely.geometry import GeometryCollection, box
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.svgLib.path import parse_path
from fontTools.fontBuilder import FontBuilder
from fontTools.ttLib import TTFont, newTable
from fontTools.ttLib.tables.O_S_2f_2 import Panose
import build_family as base
from build_fonts import to_glyph

CELL=1536
MARGIN=90
CUSTOM={
 'i':['M 160 1010 L 440 1070 L 425 80','M 135 65 L 750 120'],
 'l':['M 155 1460 L 425 1515 L 390 230 L 510 80 L 785 155'],
 'm':['M 165 20 L 180 1070',
      'M 180 715 L 345 1060 L 455 1020 L 615 820 L 605 20',
      'M 615 760 L 795 1080 L 930 1020 L 1090 820 L 1075 20'],
 'M':['M 135 65 L 180 1420 L 630 600 L 1070 1420 L 1120 65'],
 'W':['M 110 1420 L 300 75 L 625 1175 L 925 75 L 1190 1420'],
 'w':['M 110 1070 L 295 80 L 610 970 L 915 80 L 1190 1070'],
 'Q':[base.cairn.CAPO,'M 690 390 L 1035 -115'],
 '-':['M 180 640 L 1120 680'],
 '−':['M 180 640 L 1120 680'],
 '+':['M 180 640 L 1120 680','M 650 1105 L 650 210'],
 '=':['M 180 865 L 1120 905','M 180 415 L 1120 455'],
}

def transform_paths(paths,sx):
    out=[]
    for path in paths:
        pen=SVGPathPen(None)
        parse_path(path,TransformPen(pen,(sx,0,0,1,0,0)))
        out.append(pen.getCommands())
    return out

def draw(ch,bold,italic):
    overrides={ch:CUSTOM[ch]} if ch in CUSTOM else None
    g=base.draw(ch,bold,italic,overrides)
    if ch=='i':
        # Move the original diamond dot to the new, central stem.
        from shapely.ops import unary_union
        g=unary_union([affinity.translate(p,xoff=215) if p.bounds[1]>1250 else p for p in base.polygons(g)])
    # Refit the skeleton before applying the cutter: keep stroke weight.
    width=g.bounds[2]-g.bounds[0]
    if width>CELL-2*MARGIN:
        paths=CUSTOM.get(ch,base.PATHS.get(ch))
        if paths and ch not in '…©¨':
            sx=1.0
            for _ in range(5):
                width=g.bounds[2]-g.bounds[0]
                if width<=CELL-2*MARGIN:break
                sx*=min(.98,(CELL-2*MARGIN-380)/(width-380))
                g=base.draw(ch,bold,italic,{ch:transform_paths(paths,sx)})
    width=g.bounds[2]-g.bounds[0]
    if width>CELL-2*MARGIN:
        # Composite marks (ellipsis/copyright) have no single skeleton.
        g=affinity.scale(g,xfact=(CELL-2*MARGIN)/width,origin=(0,0))
    if ch.isdigit():
        _,y0,_,y1=g.bounds
        g=affinity.translate(g,yoff=-y0)
        g=affinity.scale(g,yfact=1390/(y1-y0),origin=(0,0))
    x0,_,x1,_=g.bounds
    return affinity.translate(g,xoff=(CELL-(x1-x0))/2-x0)

def build(root):
    (root/'desktop').mkdir(parents=True,exist_ok=True)
    (root/'web/fonts').mkdir(parents=True,exist_ok=True)
    repertoire=set(range(32,127))|base.SYMBOLS|set(base.ADDITIONS)|{0x201C,0x201D,0x201E}
    cmap={cp:base.UV2AGL.get(cp,f'uni{cp:04X}') for cp in sorted(repertoire)}
    order=['.notdef','.null','nonmarkingreturn']+list(dict.fromkeys(cmap.values()))
    reverse={v:chr(k) for k,v in cmap.items()};reports=[]
    for key,weight,italic in base.STYLES:
        glyphs={};metrics={}
        for name in order:
            ch=reverse.get(name,'')
            if name=='.notdef':g=box(260,0,1276,1400).difference(box(390,130,1146,1270))
            elif not ch or ch in ' \u00a0':g=GeometryCollection()
            else:g=draw(ch,weight==700,italic)
            glyphs[name]=to_glyph(g)
            metrics[name]=(CELL,round(g.bounds[0]) if not g.is_empty else 0)
        style='Bold Italic' if key=='BoldItalic' else key
        fb=FontBuilder(2048,isTTF=True)
        fb.setupGlyphOrder(order);fb.setupCharacterMap(cmap);fb.setupGlyf(glyphs)
        fb.setupHorizontalMetrics(metrics)
        fb.setupHorizontalHeader(ascent=1800,descent=-600,lineGap=80,caretSlopeRise=1000,caretSlopeRun=158 if italic else 0)
        fb.setupNameTable({'familyName':'Cairn Mono','styleName':style,'typographicFamily':'Cairn Mono','typographicSubfamily':style,
          'uniqueFontIdentifier':f'Cairn Mono 1.000 {style}', 'fullName':f'Cairn Mono {style}',
          'psName':f'CairnMono-{key}','version':'Version 1.000',
          'copyright':'Cairn design project, 2026. All included glyphs drawn for this project.',
          'description':'Carved monospace companion for code. All advances 1536/2048 em; no kerning or ligatures.',
          'licenseDescription':'No distribution license specified. All glyphs generated from included drawing source.'})
        bold=weight==700
        panose=Panose();panose.bFamilyType=2;panose.bProportion=9
        fb.setupOS2(version=4,sTypoAscender=1800,sTypoDescender=-600,sTypoLineGap=80,
          usWinAscent=1900,usWinDescent=650,sxHeight=1110,sCapHeight=1510,
          usWeightClass=weight,usWidthClass=5,fsSelection=(0x20 if bold else 0)|(1 if italic else 0)|(0x40 if not bold and not italic else 0)|0x80,
          fsType=0,yStrikeoutSize=90,yStrikeoutPosition=570,panose=panose)
        fb.setupPost(italicAngle=-9 if italic else 0,isFixedPitch=1,underlinePosition=-230,underlineThickness=85)
        fb.setupMaxp();fb.font['head'].macStyle=(1 if bold else 0)|(2 if italic else 0)
        fb.font.recalcTimestamp=False;fb.font['head'].created=fb.font['head'].modified=3875904000
        gasp=newTable('gasp');gasp.gaspRange={65535:0x000A};fb.font['gasp']=gasp
        path=root/'desktop'/f'CairnMono-{key}.ttf';fb.save(path)
        web=TTFont(path,recalcTimestamp=False);web.flavor='woff';web.save(root/'web/fonts'/f'CairnMono-{key}.woff')
        reports.append(dict(style=style,characters=len(cmap),glyphs=len(order),cell=CELL,sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
        print('Built Cairn Mono '+style,flush=True)
    (root/'mono-build-report.json').write_text(json.dumps(reports,indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path(__file__).resolve().parent.parent)
    build(p.parse_args().output)
