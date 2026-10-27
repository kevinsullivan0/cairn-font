from pathlib import Path
import argparse
import json
from PIL import ImageFont, features
from shapely import affinity
from fontTools.ttLib import TTFont
from build_fonts import FlattenPen, geometry, polygons, validate_font

def pair_adjustment(font, a, b):
    total = 0
    for lookup in font['GPOS'].table.LookupList.Lookup:
        assert lookup.LookupType == 2
        for table in lookup.SubTable:
            if a not in table.Coverage.glyphs:
                continue
            if table.Format == 1:
                records = table.PairSet[table.Coverage.glyphs.index(a)].PairValueRecord
                for record in records:
                    if record.SecondGlyph == b:
                        total += getattr(record.Value1, 'XAdvance', 0)
                        break
            else:
                assert table.Format == 2
                c1 = table.ClassDef1.classDefs.get(a, 0)
                c2 = table.ClassDef2.classDefs.get(b, 0)
                total += getattr(table.Class1Record[c1].Class2Record[c2].Value1, 'XAdvance', 0)
    return total
