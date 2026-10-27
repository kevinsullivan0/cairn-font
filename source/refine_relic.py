"""Relic II: curved bowls, cut shoulders, and geometry-informed spacing.

Retains the earlier Relic as a separate font. Run after carved_fonts.py.
"""
from pathlib import Path
import argparse
import json
import math
import numpy as np
from shapely import affinity
from shapely.geometry import Polygon, MultiPoint, LineString, GeometryCollection
from shapely.ops import unary_union
from fontTools.ttLib import TTFont
from fontTools.fontBuilder import FontBuilder
from fontTools.feaLib.builder import addOpenTypeFeaturesFromString
from fontTools.svgLib.path import parse_path
from build_fonts import FlattenPen, geometry, to_glyph, validate_font
from carved_fonts import PATHS as FIRST_PATHS, nib_points, dot
ROOT = Path(__file__).resolve().parent
LEFT = 'M 850 825 L 700 1000 Q 510 1090 350 950 C 105 800 110 450 210 260 L 370 100 Q 650 25 840 300'
RIGHT = 'M 190 795 Q 405 1115 685 1005 C 955 900 1020 580 885 310 Q 710 25 440 90 L 190 270'
OVAL = 'M 485 70 C 245 35 105 240 135 550 Q 155 875 365 1050 L 700 955 C 895 865 950 640 860 345 Q 760 65 485 70 Z'
CAP_OVAL = 'M 610 65 C 285 20 90 370 145 805 Q 190 1220 510 1440 L 835 1395 C 1150 1250 1210 845 1090 425 L 870 150 Q 745 20 610 65 Z'
CAP_BOWL = 'M 245 1390 L 650 1420 L 905 1270 C 1120 1090 1080 965 930 850 Q 745 675 220 755'
PATHS = dict(FIRST_PATHS)
PATHS.update({'a': [LEFT, 'M 865 1055 L 825 195 Q 825 55 985 145'], 'b': ['M 170 65 L 210 650 L 190 1060 L 250 1525', RIGHT], 'c': ['M 885 905 L 700 1045 L 450 1000 C 235 965 130 750 130 560 C 80 245 270 25 575 90 Q 755 135 885 275'], 'd': [LEFT, 'M 830 65 L 875 670 L 850 1075 L 915 1525'], 'e': ['M 155 520 L 855 650 L 825 865 L 665 1045 C 325 1120 120 860 130 510 C 135 210 340 25 615 95 L 890 275'], 'f': ['M 265 -125 L 320 1165 C 340 1460 570 1580 810 1385', 'M 85 975 L 720 1055'], 'g': ['M 510 590 C 275 580 155 790 275 965 L 485 1060 Q 645 1100 710 1000 C 920 825 785 610 510 590 Z', 'M 700 1005 L 915 1090', 'M 360 640 Q 185 415 445 280', 'M 445 280 C 190 295 70 35 155 -180 L 350 -345 C 585 -425 725 -330 830 -185 C 985 25 845 220 655 260 Z'], 'h': ['M 170 0 L 210 620 L 195 1060 L 250 1525', 'M 200 780 Q 375 1060 565 1030 C 800 1010 915 850 875 665 L 845 0'], 'i': ['M 255 0 L 285 525 L 270 805 L 310 1045'], 'j': ['M 375 1045 L 330 -125 Q 300 -445 20 -385 L -85 -300'], 'k': ['M 170 0 L 210 620 L 195 1060 L 250 1525', 'M 190 430 L 500 710 L 850 1045', 'M 470 690 Q 665 390 780 200 L 970 75'], 'l': ['M 265 1525 L 215 1010 L 235 690 L 195 250 Q 185 40 450 155'], 'm': ['M 170 0 L 205 515 L 190 810 L 225 1045', 'M 205 780 Q 385 1110 585 1010 Q 800 925 755 650 L 725 0', 'M 770 780 Q 990 1100 1210 995 C 1410 900 1415 750 1380 560 L 1360 0'], 'n': ['M 170 0 L 205 515 L 190 810 L 225 1045', 'M 205 780 Q 375 1060 565 1030 C 800 1010 915 850 875 665 L 845 0'], 'o': [OVAL], 'p': ['M 150 -425 L 195 340 L 180 750 L 230 1045', RIGHT], 'q': [LEFT, 'M 870 1055 L 835 700 L 855 360 L 820 -295 Q 820 -420 1035 -365'], 'r': ['M 170 0 L 205 515 L 190 810 L 225 1045', 'M 205 780 L 405 1030 L 595 980 L 800 880'], 's': ['M 855 935 L 680 1055 C 410 1135 145 915 220 765 L 505 590 C 755 500 910 305 735 145 L 535 70 Q 335 40 150 235'], 't': ['M 350 1390 L 300 305 Q 270 15 685 160', 'M 85 980 L 740 1065'], 'u': ['M 205 1045 L 170 425 C 130 105 390 -20 635 125 L 855 340', 'M 915 1045 L 860 215 Q 850 60 1000 145'], 'v': ['M 110 1045 L 290 600 L 465 70 L 995 1045'], 'w': ['M 105 1045 Q 265 500 345 70 L 770 970 Q 940 450 1050 65 L 1495 1045'], 'x': ['M 125 1045 Q 500 555 905 70', 'M 945 1045 L 110 65'], 'y': ['M 110 1045 Q 340 520 510 75', 'M 995 1045 L 530 -40 Q 340 -475 75 -335'], 'z': ['M 140 1000 Q 500 1075 930 1040 L 155 80 Q 575 25 995 160'], 'A': ['M 85 65 L 710 1470 L 1195 65', 'M 330 550 Q 665 545 995 630'], 'B': ['M 210 65 L 275 1410', CAP_BOWL, 'M 220 755 Q 755 860 975 595 C 1280 210 805 5 215 80'], 'C': ['M 1115 1240 L 845 1450 L 530 1370 C 250 1240 160 1040 135 760 C 60 350 340 -20 735 80 L 1115 330'], 'D': ['M 210 70 L 275 1410 Q 660 1510 980 1210 L 1125 980 C 1250 680 1010 270 760 115 L 210 70'], 'G': ['M 1115 1240 L 845 1450 L 530 1370 C 250 1240 160 1040 135 760 C 60 350 340 -20 735 80 L 1085 300 L 1110 720 L 735 665'], 'J': ['M 175 1400 L 1000 1445', 'M 755 1420 L 710 315 C 675 -60 355 -185 105 100 L 45 245'], 'O': [CAP_OVAL], 'P': ['M 210 65 L 275 1410', CAP_BOWL], 'Q': [CAP_OVAL, 'M 690 400 Q 840 100 1050 -110 L 1350 -170'], 'R': ['M 210 65 L 275 1410', CAP_BOWL, 'M 655 760 Q 835 370 1010 195 L 1235 70'], 'S': ['M 1055 1240 L 825 1440 C 455 1555 110 1235 225 1010 C 355 785 700 765 925 510 C 1160 170 650 -95 300 145 L 125 320'], 'U': ['M 245 1415 L 205 515 C 140 55 605 -95 905 235 Q 1090 425 1110 835 L 1140 1415'], '0': ['M 510 70 C 235 20 105 420 175 860 Q 225 1175 450 1310 L 690 1275 C 945 1090 995 610 830 280 Q 710 55 510 70 Z', 'M 290 270 L 795 1130'], '2': ['M 155 1080 C 380 1470 855 1355 940 1040 Q 1010 825 675 535 L 160 85 Q 575 25 990 140'], '3': ['M 165 1150 Q 540 1505 805 1220 C 1015 990 825 760 500 695 C 905 690 1080 335 805 140 Q 510 -65 140 270'], '5': ['M 955 1300 L 280 1280 L 225 755 Q 660 940 880 590 C 1120 225 595 -135 140 260'], '6': ['M 925 1235 Q 650 1485 345 1060 C 95 700 80 340 290 140 C 580 -110 980 165 870 580 Q 780 945 405 760 L 175 535'], '8': ['M 510 735 C 205 850 135 1080 335 1235 Q 590 1460 820 1205 C 1030 950 800 805 510 735 C 205 605 60 375 245 175 Q 510 -75 810 160 C 1080 390 840 635 510 735 Z'], '9': ['M 165 160 Q 455 -100 770 330 C 1015 690 1030 1040 815 1240 C 525 1490 125 1215 235 800 Q 325 435 700 620 L 925 845'], '?': ['M 130 1175 C 370 1515 805 1330 780 1070 Q 775 865 490 755 Q 325 680 345 425'], '(': ['M 635 1490 C 210 1150 100 395 510 -235'], ')': ['M 125 1490 C 550 1150 660 395 250 -235'], '&': ['M 1155 900 L 630 185 C 300 -140 15 180 170 470 L 630 1020 Q 825 1295 510 1415 Q 130 1360 300 1010 Q 610 515 1100 110']})

def bearings(ch):
    if ch and ch in 'acegosCGOQS0689':
        return (40, 45)
    if ch and ch in 'bpdq':
        return (60, 45)
    if ch and ch in 'hnmu':
        return (60, 65)
    if ch == 'r':
        return (60, 15)
    if ch == 'f':
        return (35, 10)
    if ch == 'l':
        return (45, 25)
    if ch and ch in 'vwyVWAY':
        return (35, 35)
    if ch and ch in '.,:;':
        return (85, 110)
    if ch and ch in 'TFL':
        return (55, 20)
    return (55, 60)

def optical_kerning(geometries, metrics, cmap, *, lower_target=240, other_target=200, punct_target=150, minimum_gap=100, maximum_positive=120, chars=None, enforce_all_pairs=False, lower_limit=-160, other_limit=-260):
    """Fit pair spaces from body silhouettes, constrained by actual ink gaps."""
    chars = chars or 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,:;!?()'
    ys = np.linspace(110, 1420, 39)
    profiles = {}
    for ch in chars:
        g = geometries[cmap[ord(ch)]]
        left = []
        right = []
        for y in ys:
            cut = g.intersection(LineString([(-3000, y), (5000, y)]))
            left.append(cut.bounds[0] if not cut.is_empty else np.nan)
            right.append(cut.bounds[2] if not cut.is_empty else np.nan)
        profiles[ch] = (np.array(left), np.array(right))
    pairs = {}
    safety = []
    for a in chars:
        for b in chars:
            if a in '.,:;!?()' and b in '.,:;!?()':
                continue
            na, nb = (cmap[ord(a)], cmap[ord(b)])
            gap = metrics[na][0] + profiles[b][0] - profiles[a][1]
            samples = gap[np.isfinite(gap)]
            if len(samples) < 5 and (not enforce_all_pairs):
                continue
            target = lower_target if a.islower() and b.islower() else other_target if a.isalnum() and b.isalnum() else punct_target
            limit = lower_limit if a.islower() and b.islower() else other_limit
            change = int(round(np.clip(target - np.quantile(samples, 0.3), limit, maximum_positive) / 5) * 5) if len(samples) >= 5 else 0
            candidate = affinity.translate(geometries[nb], xoff=metrics[na][0] + change)
            while geometries[na].distance(candidate) < minimum_gap and change < maximum_positive + 120:
                change += 5
                candidate = affinity.translate(geometries[nb], xoff=metrics[na][0] + change)
            distance = geometries[na].distance(candidate)
            assert distance >= minimum_gap - 0.5, (a + b, distance)
            safety.append(distance)
            if change:
                pairs[na, nb] = change
    return (pairs, {'pair_count': len(pairs), 'minimum_tested_ink_gap': round(min(safety), 2), 'tested_pairs': len(safety), 'method': 'body silhouette quantiles, bounded adjustments, exact outline clearance', 'lowercase_target': lower_target, 'other_alphanumeric_target': other_target, 'minimum_source_gap': minimum_gap})
