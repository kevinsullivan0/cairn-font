"""Cairn V: clipped stone crowns, rising blade heads, and open interior joins."""
from pathlib import Path
import argparse
from shapely.geometry import Polygon, Point, LineString
from shapely import affinity
from shapely.ops import unary_union
from build_fonts import polygons, FlattenPen
from fontTools.svgLib.path import parse_path
import cairn
import cairn_iv as previous
import cairn_iii as small_text
import refine_relic as base
PATHS = dict(previous.PATHS)
SHOULDER = 'M 205 650 Q 350 1005 500 1080 L 650 1075 L 790 860 L 870 570 L 835 20'
RIGHT = 'M 205 750 L 455 1045 L 610 1060 Q 765 1045 865 825 C 1030 535 850 155 565 85 Q 325 30 195 290'
PATHS.update({'h': [previous.PATHS['h'][0], SHOULDER], 'n': [previous.PATHS['n'][0], SHOULDER], 'm': [previous.PATHS['m'][0], 'M 205 650 Q 345 1000 480 1080 L 600 1075 L 725 885 L 770 570 L 735 20', 'M 765 650 Q 925 1005 1075 1080 L 1225 1075 L 1355 860 L 1415 570 L 1380 20'], 'b': [previous.PATHS['b'][0], RIGHT], 'p': [previous.PATHS['p'][0], RIGHT], 'A': ['M 95 65 L 390 850 L 620 1445 L 690 1475 L 920 785 L 1180 65', previous.PATHS['A'][1]], 's': ['M 830 910 L 625 1080 L 465 1070 Q 250 1035 185 865 Q 145 750 345 610 L 665 415 Q 945 225 690 110 C 475 15 280 70 145 245']})
HEAD = [(-160, -35), (-95, 30), (215, 140), (95, -45)]
