"""Cairn IV: prose rhythm, cleaner overhangs, and deliberate cut shoulders."""
from pathlib import Path
import argparse
from shapely import affinity
import cairn_iii as previous
import refine_relic as base
PATHS = dict(previous.PATHS)
PATHS.update({'a': ['M 190 940 L 355 1085 Q 555 1180 760 1020 L 845 795 L 825 20', 'M 825 690 L 525 710 C 215 745 90 465 190 260 Q 385 -65 815 335'], 'r': [previous.PATHS['r'][0], 'M 205 705 L 440 1065 Q 600 1090 690 900'], 'f': ['M 275 -140 L 315 655 L 270 1090 Q 280 1450 500 1490 L 680 1340', 'M 85 885 L 380 975 L 650 1010'], 't': ['M 375 1390 L 330 290 L 430 105 L 650 180', 'M 95 910 L 370 990 L 690 1040'], 'g': [previous.PATHS['g'][0], 'M 865 1080 L 845 30 L 795 -230 Q 595 -495 335 -385 L 165 -265'], 'k': [previous.PATHS['k'][0], previous.PATHS['k'][1], 'M 520 690 L 745 295 L 1010 80'], 'R': [previous.PATHS['R'][0], previous.PATHS['R'][1], 'M 625 775 L 830 390 L 1040 90 L 1250 155'], 'Q': [previous.PATHS['Q'][0], 'M 650 420 L 990 -5 L 1265 -145 L 1460 -70']})
