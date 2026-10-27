"""Validate the delivered font family, including web round trips and shaping."""
from pathlib import Path
import json,hashlib,argparse
import numpy as np
from scipy.ndimage import label,binary_fill_holes
from PIL import ImageFont,features
from shapely import affinity
from shapely.geometry import Polygon
from fontTools.ttLib import TTFont
from build_fonts import FlattenPen,geometry,polygons
from check_relic import pair_adjustment
from build_family import STYLES

def validate(root):
    assert features.check('raqm')
    reports=[];coverage=None
    for key,weight,italic in STYLES:
        path=root/'desktop'/f'Cairn-{key}.ttf';f=TTFont(path,checkChecksums=2)
        cm=f.getBestCmap();gs=f.getGlyphSet()
        if coverage is None:coverage=set(cm)
        assert coverage==set(cm)
        assert set(range(32,127))<=set(cm),'Incomplete printable ASCII'
        assert {160,0x2018,0x2019,0x2013,0x2014,0x2026,0x2022,0x2212}<=set(cm)
        assert f['name'].getDebugName(1)=='Cairn'
        assert f['name'].getDebugName(2)==('Bold Italic' if key=='BoldItalic' else key)
        assert f['OS/2'].usWeightClass==weight
        assert f['OS/2'].fsSelection&0x80
        assert bool(f['OS/2'].fsSelection&1)==italic
        assert bool(f['OS/2'].fsSelection&32)==(weight==700)
        assert bool(f['head'].macStyle&2)==italic
        assert bool(f['head'].macStyle&1)==(weight==700)
        assert f['post'].italicAngle==(-9 if italic else 0)
        shapes={}
        for cp,name in cm.items():
            pen=FlattenPen(gs);gs[name].draw(pen);g=geometry(pen);shapes[chr(cp)]=g
            if not g.is_empty:
                x0,y0,x1,y1=g.bounds;advance,lsb=f['hmtx'][name]
                assert 0<=x0<=x1<=advance,(key,cp,'horizontal extent')
                assert -600<=y0<=y1<=1800,(key,cp,'line clipping',g.bounds)
                assert abs(lsb-x0)<=1
            else:assert cp in {32,160},(key,cp,'Empty mapped glyph')
        assert f['hmtx'][cm[32]]==f['hmtx'][cm[160]]
        assert not any(0xE000<=cp<=0xF8FF for cp in cm),'Unexpected retained ornament'
        expected={ch:1 for ch in 'ADOPQRabdegopq469'};expected.update({'B':2,'0':2,'8':2})
        for ch in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789':
            pieces=[p for p in polygons(shapes[ch]) if p.area>80]
            counters=sum(sum(Polygon(r).area>80 for r in p.interiors) for p in pieces)
            assert counters==expected.get(ch,0),(key,'counter',ch,counters)
            assert len(pieces)==(2 if ch in 'ij' else 1),(key,'components',ch,len(pieces))
        chars=''.join(chr(cp) for cp in sorted(cm) if cp<0xE000 and cp not in {32,160,168})
        minimum=99999;count=0;tightest=''
        for a in chars:
            for b in chars:
                if a in '.,:;!?()' and b in '.,:;!?()':continue
                na,nb=cm[ord(a)],cm[ord(b)];shift=f['hmtx'][na][0]+pair_adjustment(f,na,nb)
                distance=shapes[a].distance(affinity.translate(shapes[b],xoff=shift))
                assert distance>=138,(key,a+b,distance)
                if distance<minimum:minimum=distance;tightest=a+b
                count+=1
        raster=ImageFont.truetype(str(path),128)
        pairs=['AV','To','Ta','rn','nn','oo','fi','ff','“T','d”','”a',"f'",'a-','(e','e)',':a','a—','s…','’s','[a','a]','@a']
        for pair in pairs:
            adjustment=pair_adjustment(f,cm[ord(pair[0])],cm[ord(pair[1])])
            actual=raster.getlength(pair,features=['kern'])-raster.getlength(pair,features=['-kern'])
            assert abs(actual-adjustment/16)<.04,(key,pair,actual,adjustment/16)
        widths=[raster.getlength(str(i),features=['tnum']) for i in range(10)]
        assert max(widths)-min(widths)<.02,(key,'tabular figures')
        for sample in ['11111','88888','01234','56789']:
            assert abs(raster.getlength(sample,features=['tnum'])-5*widths[0])<.04
        dots=0;counters=0
        for size in [12,14,16,18,20]:
            native=ImageFont.truetype(str(path),size)
            for ch in 'ijaeog':
                mask=native.getmask(ch,mode='L');ink=np.pad(np.asarray(mask).reshape(mask.size[1],mask.size[0])>=128,3)
                if ch in 'ij':
                    assert label(ink,structure=np.ones((3,3)))[1]==2,(key,'dot',ch,size)
                    dots+=1
                elif size>=14:
                    white=binary_fill_holes(ink)&~ink
                    assert white.sum()>=5,(key,'raster counter',ch,size,white.sum())
                    counters+=1
        # The WOFF must decode to the same metrics, contours, features and style data.
        w=TTFont(root/'web/fonts'/f'Cairn-{key}.woff')
        assert w.getBestCmap()==cm
        for table in ['glyf','hmtx','GPOS','GSUB','name','OS/2','post','gasp']:
            assert w.getTableData(table)==f.getTableData(table),(key,'web roundtrip',table)
        # All glyphs rasterize, including the alternate ornament and punctuation set.
        for cp in cm:
            assert raster.getmask(chr(cp)).getbbox() is not None or chr(cp).isspace(),(key,cp)
        report={'style':key,'status':'passed','characters':len(cm),'glyphs':len(f.getGlyphOrder()),
          'pair_clearances':count,'minimum_gap':round(minimum,2),'tightest_pair':tightest,
          'shaping_pairs':len(pairs),'letter_digit_topologies':62,'dot_raster_checks':dots,
          'counter_raster_checks':counters,'tabular_digits':10,'woff_roundtrip':'identical tables',
          'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'ttf_bytes':path.stat().st_size,
          'woff_bytes':(root/'web/fonts'/f'Cairn-{key}.woff').stat().st_size}
        reports.append(report);print(json.dumps(report),flush=True)
    (root/'validation.json').write_text(json.dumps({'status':'passed','styles':reports,
      'scope':'Serialized outline, metadata, OpenType shaping and Pillow/FreeType raster checks; no browser or OS installation verification. No manual TrueType hinting.'},indent=2)+'\n')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('root',type=Path,nargs='?',default=Path(__file__).resolve().parent.parent)
    validate(p.parse_args().root)
