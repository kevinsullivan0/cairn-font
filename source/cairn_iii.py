"""Cairn III: a small-text refinement of Cairn II, preserving its architecture."""
from pathlib import Path
import argparse
import math
from shapely.geometry import Polygon
from shapely.ops import unary_union
from build_fonts import polygons
import cairn
import cairn_ii as previous
import refine_relic as base
PATHS = dict(previous.PATHS)
PATHS.update({'c': ['M 875 865 L 640 1080 C 280 1135 95 860 140 525 C 175 205 390 25 640 95 L 880 275'], 'e': ['M 145 465 L 890 675 L 820 890 L 615 1080 C 270 1080 90 815 145 480 C 200 175 410 20 665 100 L 910 275']})

def bearings(ch):
    left, right = base.bearings(ch)
    return (left + 10, right + 15)
