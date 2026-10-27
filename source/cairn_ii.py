"""Cairn II: Cairn's anatomy with disciplined stems and E2-style cut serifs."""
from pathlib import Path
import argparse
import math
from shapely.geometry import Polygon, MultiPoint
from shapely.ops import unary_union
from carved_fonts import nib_points
from build_fonts import polygons
import cairn
import refine_relic as base
PATHS = dict(cairn.PATHS)
STEM = 'M 200 20 L 220 1070'
TALL = 'M 200 20 L 215 930 L 245 1515'
for ch in 'bhk':
    PATHS[ch] = [TALL, *PATHS[ch][1:]]
for ch in 'mnr':
    PATHS[ch] = [STEM, *PATHS[ch][1:]]
PATHS.update({'a': ['M 175 900 Q 430 1205 755 1020 L 845 795 L 825 20', cairn.PATHS['a'][1]], 'd': [cairn.LEFT, 'M 845 20 L 860 1070 L 920 1515'], 'g': [cairn.LEFT, 'M 865 1080 L 845 30 L 775 -230 Q 575 -510 295 -340 L 145 -205'], 'i': ['M 220 20 L 235 1070'], 'j': ['M 335 1070 L 320 -125 Q 295 -420 80 -390 L -60 -255'], 'l': ['M 240 1515 L 205 210 L 310 85 L 470 145'], 'p': ['M 185 -420 L 210 1070', cairn.RIGHT], 'q': [cairn.LEFT, 'M 865 1080 L 850 -220 L 1080 -370'], 't': ['M 375 1390 L 330 290 L 430 105 L 710 205', cairn.PATHS['t'][1]], 'u': ['M 200 1070 L 195 365 Q 205 100 445 75 L 830 385', 'M 870 1070 L 850 20'], 'v': ['M 110 1070 L 460 80 L 985 1070'], 'w': ['M 110 1070 L 375 80 L 795 1000 L 1050 80 L 1530 1070'], 'x': ['M 130 1070 L 925 65', 'M 940 1070 L 110 65'], 'y': ['M 110 1070 L 505 85', cairn.PATHS['y'][1]], 'z': ['M 130 1000 L 915 1040 L 155 100 L 990 180'], 'H': ['M 210 65 L 235 1420', 'M 1100 65 L 1120 1420', cairn.PATHS['H'][2]], 'I': [cairn.PATHS['I'][0], 'M 480 1410 L 460 80', cairn.PATHS['I'][2]], 'J': [cairn.PATHS['J'][0], 'M 770 1410 L 745 365 Q 665 -95 300 20 L 105 240'], 'K': ['M 210 65 L 235 1420', *cairn.PATHS['K'][1:]], 'E': ['M 1070 1430 L 270 1380 L 210 80 L 1120 170', cairn.PATHS['E'][1]], 'L': ['M 270 1420 L 210 80 L 1120 170'], 'T': [cairn.PATHS['T'][0], 'M 665 1430 L 650 65'], 'U': ['M 235 1420 L 215 460 Q 235 65 580 70 L 950 320 Q 1100 475 1090 810 L 1140 1420'], 'V': ['M 120 1420 L 565 75 L 1225 1420'], 'W': ['M 105 1420 L 435 75 L 995 1340 L 1330 75 L 1860 1420'], 'X': ['M 140 1420 L 1155 65', 'M 1165 1420 L 105 65'], 'Z': ['M 150 1380 L 1170 1420 L 155 100 L 1210 185'], '1': ['M 120 960 L 535 1300 L 525 80', cairn.PATHS['1'][1]]})

def stroke(points, weight=1, blade=False, *, nib=None, blade_length=145, blade_width=45, head=None, terminal_ends=(True, True)):
    nib = nib if nib is not None else nib_points(1, weight * 0.98)
    shapes = [MultiPoint([(x + dx, y + dy) for x, y in (p, q) for dx, dy in nib]).convex_hull for p, q in zip(points, points[1:]) if p != q]
    if points[0] != points[-1]:
        for enabled, (p, q) in zip(terminal_ends, [(points[0], points[1]), (points[-1], points[-2])]):
            if not enabled:
                continue
            x, y = p
            if abs(q[1] - y) > 1.8 * abs(q[0] - x):
                if y > q[1]:
                    cap = [(x + dx, y + dy) for dx, dy in head] if head is not None else [(x - 160, y - 35), (x - 95, y + 30), (x + 225, y + 115), (x + 95, y - 45)]
                else:
                    cap = [(x - 190, y - 35), (x - 70, y - 75), (x + 205, y + 60), (x + 75, y + 10)]
                shapes.append(Polygon(cap))
            elif blade:
                dx, dy = (x - q[0], y - q[1])
                length = math.hypot(dx, dy)
                if length:
                    ux, uy = (dx / length, dy / length)
                    shapes.append(Polygon([(x - uy * blade_width, y + ux * blade_width), (x + uy * blade_width, y - ux * blade_width), (x + ux * blade_length, y + uy * blade_length)]))
    return unary_union(shapes)
