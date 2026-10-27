"""Build three personal Elbjorg studies. Original font remains untouched.

Python 3.12+: fonttools, shapely, numpy, scipy, scikit-image, Pillow.
Run: python build_fonts.py --source /path/to/ElbjorgScript.ttf
The file is a design study: no claim of proven reading-speed improvement.
"""
from pathlib import Path
import argparse
import hashlib
import json
import logging
import math
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage
from skimage.morphology import medial_axis
from skimage.measure import find_contours, approximate_polygon
from shapely import affinity
from shapely.geometry import Polygon, LineString, GeometryCollection, box
from shapely.ops import unary_union
from fontTools.fontBuilder import FontBuilder
from fontTools.pens.basePen import BasePen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.pens.boundsPen import BoundsPen
from fontTools.svgLib.path import parse_path
from fontTools.ttLib import TTFont
logging.getLogger('fontTools.ttLib.tables._h_e_a_d').setLevel(logging.ERROR)
ROOT = Path(__file__).resolve().parent
UPM = 2048

class FlattenPen(BasePen):
    """Sample curves finely enough to preserve outlines at text sizes."""

    def __init__(self, glyphset=None, step=9):
        super().__init__(glyphset)
        self.contours = []
        self.points = []
        self.step = step

    def _moveTo(self, p):
        if self.points:
            self._endPath()
        self.points = [p]

    def _lineTo(self, p):
        self.points.append(p)

    def _qCurveToOne(self, p1, p2):
        p0 = self.points[-1]
        n = max(3, math.ceil((math.dist(p0, p1) + math.dist(p1, p2)) / self.step))
        for t in np.linspace(0, 1, n + 1)[1:]:
            self.points.append(tuple(((1 - t) ** 2 * p0[i] + 2 * (1 - t) * t * p1[i] + t * t * p2[i] for i in (0, 1))))

    def _curveToOne(self, p1, p2, p3):
        p0 = self.points[-1]
        n = max(4, math.ceil(sum((math.dist(a, b) for a, b in zip([p0, p1, p2], [p1, p2, p3]))) / self.step))
        for t in np.linspace(0, 1, n + 1)[1:]:
            self.points.append(tuple(((1 - t) ** 3 * p0[i] + 3 * (1 - t) ** 2 * t * p1[i] + 3 * (1 - t) * t * t * p2[i] + t ** 3 * p3[i] for i in (0, 1))))

    def _closePath(self):
        if self.points and self.points[0] != self.points[-1]:
            self.points.append(self.points[0])
        self._endPath()

    def _endPath(self):
        if len(self.points) > 1:
            self.contours.append(self.points)
        self.points = []

def geometry(pen):
    result = GeometryCollection()
    for contour in pen.contours:
        if len(contour) >= 4:
            p = Polygon(contour)
            if not p.is_valid:
                p = p.buffer(0)
            result = result.symmetric_difference(p)
    return result

def polygons(g):
    if g.is_empty:
        return []
    if g.geom_type == 'Polygon':
        return [g]
    return [p for part in g.geoms for p in polygons(part)]
BOWL = 'M 540 55 L 300 65 Q 130 130 120 350 L 120 740 Q 145 970 335 1045 L 725 1045 Q 930 970 955 740 L 955 350 Q 930 120 750 65 Z'
PATHS = {'a': ['M 180 910 Q 300 1090 600 1060 Q 885 1040 890 780 L 890 50', 'M 885 680 L 495 680 Q 155 640 160 330 Q 165 65 420 60 Q 690 50 890 280'], 'b': ['M 170 50 L 170 1490', 'M 175 785 Q 350 1090 660 1045 L 800 985 Q 1010 790 940 340 Q 885 55 600 60 Q 310 50 175 250'], 'c': ['M 890 925 L 730 1030 Q 450 1130 235 925 Q 95 760 125 475 Q 140 190 350 90 Q 640 -10 900 180'], 'd': ['M 900 50 L 900 1490', 'M 890 825 Q 675 1110 390 1025 Q 95 930 115 530 Q 100 170 375 70 Q 660 -10 890 290'], 'e': ['M 145 575 L 940 575 Q 960 895 755 1015 Q 460 1160 245 940 Q 95 780 125 475 Q 145 180 375 85 Q 655 -10 900 180'], 'f': ['M 260 0 L 260 1150 Q 275 1480 620 1480 L 775 1430', 'M 65 1020 L 680 1020'], 'g': ['M 900 1030 L 900 -160 Q 880 -430 580 -450 Q 340 -450 180 -315', 'M 890 820 Q 675 1100 390 1025 Q 95 930 115 550 Q 105 210 375 100 Q 660 25 890 290'], 'h': ['M 170 0 L 170 1490', 'M 170 750 Q 365 1115 690 1030 Q 900 985 900 715 L 900 0'], 'i': ['M 220 0 L 220 1045'], 'j': ['M 340 1045 L 340 -160 Q 320 -450 35 -430 L -100 -380'], 'k': ['M 170 0 L 170 1490', 'M 170 440 L 900 1045', 'M 455 690 L 970 0'], 'l': ['M 220 1490 L 220 165 Q 230 30 420 65'], 'm': ['M 170 0 L 170 1045', 'M 170 780 Q 335 1110 600 1020 Q 765 960 765 700 L 765 0', 'M 765 780 Q 930 1110 1195 1020 Q 1370 965 1370 700 L 1370 0'], 'n': ['M 170 0 L 170 1045', 'M 170 760 Q 365 1115 690 1030 Q 900 985 900 715 L 900 0'], 'o': [BOWL], 'p': ['M 170 -440 L 170 1045', 'M 175 785 Q 350 1090 660 1045 L 800 985 Q 1010 790 940 340 Q 885 55 600 60 Q 310 50 175 250'], 'q': ['M 900 1045 L 900 -440', 'M 890 825 Q 675 1110 390 1025 Q 95 930 115 530 Q 100 170 375 70 Q 660 -10 890 290'], 'r': ['M 170 0 L 170 1045', 'M 170 760 Q 355 1145 720 990'], 's': ['M 825 925 Q 550 1160 260 965 Q 70 810 255 645 L 660 465 Q 965 315 765 120 Q 500 -70 165 155'], 't': ['M 300 1400 L 300 270 Q 310 -15 660 95', 'M 70 1010 L 710 1010'], 'u': ['M 170 1045 L 170 350 Q 160 30 485 60 Q 760 75 900 370', 'M 900 1045 L 900 50'], 'v': ['M 90 1045 L 530 60 L 970 1045'], 'w': ['M 90 1045 L 385 60 L 735 990 L 1070 60 L 1385 1045'], 'x': ['M 110 1045 L 900 50', 'M 900 1045 L 110 50'], 'y': ['M 90 1045 L 550 65', 'M 970 1045 L 440 -230 Q 325 -510 75 -390'], 'z': ['M 100 1020 L 900 1020 L 110 80 L 930 80']}

def to_glyph(g):
    from shapely.geometry.polygon import orient
    pen = TTGlyphPen(None)
    for p in polygons(g):
        p = orient(p, sign=-1)
        for ring in [p.exterior, *p.interiors]:
            pts = [(round(x), round(y)) for x, y in ring.coords[:-1]]
            pts = list(dict.fromkeys(pts))
            if len(pts) >= 3:
                pen.moveTo(pts[0])
                for pt in pts[1:]:
                    pen.lineTo(pt)
                pen.closePath()
    return pen.glyph()

def validate_font(file, cmap, order):
    """A rerunnable check of the exact font files supplied to the reader."""
    check = TTFont(file, checkChecksums=2)
    assert check.getBestCmap() == cmap
    assert check.getGlyphOrder() == order
    points = 0
    for name in order:
        glyph = check['glyf'][name]
        if glyph.numberOfContours:
            assert glyph.xMin >= 0 and glyph.xMax <= check['hmtx'][name][0], name
            assert glyph.yMin >= -600 and glyph.yMax <= 1800, (name, glyph.yMin, glyph.yMax)
            points += len(glyph.coordinates)
    testfont = ImageFont.truetype(str(file), 32)
    for cp in cmap:
        assert testfont.getmask(chr(cp)).getbbox() is not None or chr(cp).isspace(), hex(cp)
    return {'family': check['name'].getDebugName(1), 'file': file.name, 'glyphs': len(order), 'mapped_characters': len(cmap), 'contour_points': points, 'bytes': file.stat().st_size, 'sha256': hashlib.sha256(file.read_bytes()).hexdigest(), 'validation': 'passed'}
