"""Paint The Last Beacon from a blank canvas using only the local raster engine."""

from argparse import ArgumentParser
from math import exp, sin
from pathlib import Path
from random import Random

from raster import Canvas, Noise, mix, smooth


def paint(width, height, seed):
    board = Canvas(width, height)
    rng = Random(seed)
    clouds = [Noise(cols, rows, seed + layer)
              for layer, (cols, rows) in enumerate(((4, 10), (9, 25), (21, 62)))]
    ground = (21, 35, 33)
    bronze = (241, 179, 80)
    sea = (45, 81, 74)
    shadow = (18, 30, 29)
    horizon = 0.452

    def atmosphere(x, y):
        # Warp the finer grain along the storm's slanted flow.
        billows = clouds[0](x + 0.24*y, y)
        eddies = clouds[1](x + .13*(billows-.5), y)
        scumble = clouds[2](x, y)
        cloud = billows*.59 + eddies*.30 + scumble*.11
        light = exp(-((x-.63)/.46)**2 - ((y-.391)/.111)**2)
        opening = exp(-((x-.56-.71*(.38-y))/.28)**2 - ((y-.288)/.135)**2)
        cloud_break = smooth((.69-cloud)*3) * opening
        haze = exp(-abs(y-horizon)*155) * .47
        if y < horizon:
            ridge = smooth(.25 + 2.0*(cloud-.42))
            bronze_veil = (light * (.28 + .62*ridge)) * (.81 + .12*sin(y*72+x*3))
            base = mix(ground, (78, 76, 49), .44*ridge)
            warmth = min(.8, bronze_veil + .24*cloud_break)
            return mix(mix(base, bronze, warmth), (99, 108, 78), haze)
        depth = smooth((y-horizon)/.53)
        reflection = exp(-((x-.66)/(.13+depth*.23))**2 - (y-horizon)*4.9)
        base = mix(sea, shadow, .22 + depth*.73)
        base = mix(base, (173, 132, 61), reflection*(.25 + .37*cloud))
        chop = max(0, sin((y-horizon)*390/(1+depth*.7) + 7*billows))
        return mix(base, (93, 112, 97), (.015 + .115*cloud)*chop + haze)

    board.field(atmosphere)

    def ridge(points, color, alpha):
        edge = []
        for left, right in zip(points, points[1:]):
            for i in range(8):
                x, y = mix(left, right, i/8)
                noise = clouds[2](x, y + x*.6)
                edge.append((x, y + (noise-.5)*.009))
        edge.append(points[-1])
        board.polygon(edge + [(points[-1][0], .472), (points[0][0], .472)], color, alpha)

    ridge([(0,.428),(.073,.431),(.151,.421),(.27,.44),(.355,.438),(.45,.454),(.57,.45)],
          (89, 91, 63), .43)
    ridge([(.62,.455),(.744,.444),(.825,.425),(.902,.433),(.974,.416),(1,.421)],
          (81, 84, 58), .55)
    ridge([(0,.447),(.051,.449),(.103,.444),(.182,.451),(.268,.448),(.341,.46)],
          (55, 70, 58), .73)

    # Underpainting for the broken reflection of the beacon.
    for i in range(90):
        y = rng.uniform(.454, .773)
        distance = (y-horizon)/.32
        x = rng.gauss(.57-.32*distance, .021+.05*distance)
        color = mix((211,150,46), (84,113,93), distance*.65)
        board.dab(x, y, rng.uniform(.012,.059), rng.uniform(.00075,.0027),
                  color, (1-distance)*rng.uniform(.13,.62), .72)

    # Long flat marks read as waves. Group them by water depth and reflected light.
    for _ in range(660):
        y = rng.uniform(horizon+.006, .995)
        x = rng.uniform(0, 1)
        depth = smooth((y-horizon)/.53)
        light = exp(-((x-.65)/(.13+.23*depth))**2) * (1-depth)
        color = mix((76, 103, 92), (195, 145, 64), light)
        if rng.random() < .34:
            color = (19, 35, 32)
        board.dab(x, y, rng.uniform(.005,.044)*(1+depth), rng.uniform(.00055,.0015),
                  color, rng.uniform(.09,.48), .68)

    # The headland cuts into the illuminated water diagonally.
    cape = [(.314,.556),(.366,.548),(.415,.527),(.451,.522),(.481,.504),(.521,.505),
            (.565,.475),(.606,.471),(.651,.477),(.693,.489),(.748,.491),(.79,.51),
            (.849,.505),(.901,.519),(.948,.508),(1,.514),(1,.749),(.921,.718),
            (.842,.695),(.738,.679),(.641,.646),(.566,.643),(.487,.615),(.429,.598),
            (.374,.577),(.339,.571)]
    def shale(x, y):
        fault = clouds[1](x, y)
        splinter = clouds[2](x + .08*fault, y)
        seams = smooth(.48 + .56*sin((y - .086*x + .019*fault + .007*splinter)*820))
        trace = smooth((fault*.56+splinter*.44-.23)*1.8) * (.3+.55*seams)
        return mix((22, 36, 32), (68, 75, 56), trace)

    board.polygon(cape, shale, .98, .12)
    shelf = [(.321,.556),(.416,.528),(.49,.506),(.531,.503),(.57,.475),(.608,.471),
             (.656,.48),(.694,.491),(.794,.512),(.892,.525),(1,.518),(1,.584),
             (.911,.57),(.785,.572),(.702,.55),(.595,.543),(.544,.56),(.482,.562),
             (.404,.58),(.376,.575)]
    def ochre(x, y):
        fault = clouds[2](x, y)
        streak = smooth(.42 + .52*sin((y - .095*x + .015*fault)*580))
        return mix((59, 63, 42), (133, 110, 62), streak * fault*.82)

    board.polygon(shelf, ochre, .89, .15)
    board.polygon([(.33,.557),(.45,.54),(.50,.521),(.56,.513),(.61,.487),(.675,.496),
                   (.722,.512),(.681,.518),(.602,.513),(.54,.534),(.461,.551),(.385,.565)],
                  (123, 100, 56), .64)
    for _ in range(168):
        x = rng.uniform(.388, 1.04)
        top = .512 - .038*exp(-((x-.59)/.112)**2)
        bottom = .58 + .12*smooth((x-.37)/.68)
        y = rng.uniform(top+.018,bottom)
        lit = rng.random() < .29
        color = (131, 108, 61) if lit else (23, 38, 34)
        board.stroke([(x,y), (x+.034,y+.004), (x+.057,y+.0065)], color,
                     rng.uniform(.0009,.0041), rng.uniform(.12,.42), .73)

    # The remains of the seawall lead toward the cairn. Windward stones
    # catch the light, and a missing section leaves the stair exposed.
    steps = [(.91,.547),(.868,.542),(.83,.537),(.789,.532),(.747,.527),
             (.707,.519),(.665,.512)]
    for i, (x,y) in enumerate(steps):
        height = .008 + .006*rng.random()
        board.polygon([(x-.027,y), (x+.019,y-.002), (x+.027,y+height),
                       (x-.021,y+height+.003)], (38,40,29), .90)
        lip = (161,126,68) if i not in (2,3) else (95,92,56)
        board.stroke([(x-.026,y), (x,y-.002), (x+.022,y-.001)],
                     lip, .002, .57, .64)
    for x,y,h in ((.934,.549,.026),(.901,.543,.019),(.853,.54,.012),
                    (.772,.533,.015),(.734,.527,.018)):
        board.polygon([(x-.012,y),(x-.009,y-h),(x+.011,y-h+.0034),
                       (x+.015,y)], (42,45,32), .96)
        board.stroke([(x-.009,y-h),(x+.011,y-h+.0034)],(194,150,83),.002,.42,.67)
    board.dab(.754,.524,.025,.007,(233,156,40),.27)
    board.dab(.754,.5235,.004,.0013,(246,188,88),.86)

    rock_shadow = (26, 34, 29)
    stones = [
        ([(.493,.505),(.524,.485),(.643,.479),(.688,.484),(.695,.495),(.635,.509),(.551,.512)],
         [(.493,.505),(.524,.485),(.643,.479),(.676,.484),(.596,.491),(.547,.500)]),
        ([(.522,.488),(.543,.471),(.635,.465),(.672,.473),(.653,.484),(.607,.491),(.549,.495)],
         [(.522,.488),(.543,.471),(.635,.465),(.663,.471),(.597,.476),(.555,.486)]),
        ([(.547,.474),(.554,.452),(.574,.447),(.633,.447),(.659,.456),(.654,.466),(.596,.478)],
         [(.547,.474),(.554,.452),(.574,.447),(.633,.447),(.614,.457),(.577,.463)]),
        ([(.564,.453),(.573,.431),(.601,.427),(.634,.430),(.640,.440),(.619,.451),(.583,.455)],
         [(.564,.453),(.573,.431),(.601,.427),(.633,.430),(.606,.435),(.586,.445)]),
        ([(.582,.433),(.585,.410),(.600,.400),(.623,.402),(.638,.410),(.622,.429),(.606,.436)],
         [(.582,.433),(.585,.410),(.600,.400),(.625,.403),(.602,.412),(.599,.424)]),
        ([(.580,.408),(.586,.394),(.612,.388),(.643,.397),(.634,.405),(.596,.413)],
         [(.580,.408),(.586,.394),(.612,.388),(.643,.397),(.601,.401)]),
    ]
    stone_light = [(144,114,60),(168,131,69),(160,122,61),(193,146,75),(186,139,67),(214,158,79)]
    for (silhouette, face), lit in zip(stones, stone_light):
        board.polygon(silhouette, rock_shadow, .98)
        def patina(x, y):
            flake = clouds[2](x+.07, y-.003)
            seam = .72 + .19*sin(740*y+82*x+14*flake)
            return mix((74, 76, 46), lit, seam*flake+.32)
        board.polygon(face, patina, .94, .11)
        board.stroke(face[:3], (216,169,92), .0018, .25, .8)

    # Warm light in the cleft and a few sparks lifted clear of the stone.
    board.dab(.613, .389, .136, .038, (224,142,39), .21)
    board.dab(.613, .389, .066, .020, (195,123,35), .24)
    board.dab(.609, .389, .018, .005, (249,191,74), .72)
    board.stroke([(.601,.389),(.608,.381),(.615,.386),(.618,.39)], (250,205,99), .0035, .8)
    for _ in range(15):
        x = rng.gauss(.611, .042)
        y = rng.uniform(.36,.39)
        board.dab(x,y,.002,.00072,(237,169,79),rng.uniform(.23,.68), .3)

    surf = [
        [(.357,.575),(.428,.6),(.466,.607),(.528,.625),(.599,.633),(.652,.652),(.728,.665),(.809,.69),(.929,.716)],
        [(.308,.579),(.376,.603),(.439,.615),(.49,.633),(.553,.648),(.608,.657),(.682,.685),(.751,.697),(.898,.734)],
        [(.388,.621),(.445,.635),(.501,.654),(.566,.668),(.623,.691),(.691,.713),(.769,.734)],
    ]
    for i, crest in enumerate(surf):
        board.stroke(crest, (122,149,121), .0044, .35-i*.075, .72)
        for a, b in zip(crest, crest[1:]):
            for _ in range(13):
                x, y = mix(a,b,rng.random())
                board.dab(x+rng.gauss(0,.014),y+rng.gauss(0,.0031),
                          rng.uniform(.002,.016),rng.uniform(.0007,.0019),
                          (158,169,131),rng.uniform(.08,.28), .8)

    # One approaching boat. Its little lantern answers the beacon, and
    # the broken wake places its movement in the grain of the water.
    wake = [(.213,.74),(.25,.746),(.302,.756),(.345,.769),(.394,.785)]
    board.stroke(wake, (135,145,107), .0025, .41, .8)
    for a,b in zip(wake,wake[1:]):
        for _ in range(11):
            x,y = mix(a,b,rng.random())
            board.dab(x+rng.gauss(0,.019),y+rng.gauss(0,.0024),
                      rng.uniform(.002,.014),.00085,(140,154,118),.23,.8)
    board.polygon([(.146,.733),(.193,.737),(.259,.737),(.276,.732),
                   (.256,.747),(.231,.75),(.184,.744)],
                  (14,27,27), .98)
    board.stroke([(.146,.733),(.194,.737),(.257,.736),(.276,.732)],
                 (185,135,62), .0022, .7, .54)
    board.stroke([(.226,.739),(.211,.701)], (23,31,27), .0035,.95,.3)
    board.polygon([(.213,.705),(.221,.729),(.178,.729),(.193,.72),(.197,.714)],
                  (143,135,90), .69, .17)
    board.stroke([(.177,.730),(.191,.735),(.22,.737)],(74,65,43),.0018,.9,.5)
    board.dab(.25,.734,.034,.0075,(221,141,38),.27)
    board.dab(.25,.734,.005,.0015,(253,192,78),.87)
    for _ in range(14):
        y = rng.uniform(.748,.776)
        board.dab(rng.gauss(.253,.015), y, rng.uniform(.005,.018), .001,
                  (184,130,48), rng.uniform(.11,.35), .66)

    # A final broken bank of cloud just catches the light around the beacon.
    for _ in range(58):
        x = rng.uniform(.21,.94)
        y = rng.uniform(.304,.372)
        tint = mix((125,103,58),(222,163,69),rng.random())
        board.dab(x,y,rng.uniform(.01,.12),rng.uniform(.0009,.0045),tint,
                  rng.uniform(.025,.12), .72)
    return board


def paint_brass(width, height, seed, footer=False):
    board = Canvas(width, height)
    rng = Random(seed)
    clouds = Noise(15 if footer else 52, 5, seed + 807)
    speckle = Noise(79 if footer else 135, 12, seed + 110)
    low = (58, 49, 37) if footer else (74, 61, 44)
    high = (139, 110, 64) if footer else (156, 125, 77)

    def metal(x, y):
        field = clouds(x, y)
        patina = speckle(x + .022*(field-.5), y)
        shade = .21 + .28*field + .10*patina + .10*(1-y)
        if not footer:
            shade += .17*exp(-((x-.89)/.15)**2 - ((y-.42)/.44)**2)
        return mix(low, high, shade)

    board.field(metal)
    for _ in range(96 if footer else 190):
        x,y = rng.random(),rng.random()
        tint = (162,137,90) if rng.random() < .44 else (54,46,35)
        board.dab(x,y,rng.uniform(.001,.011),rng.uniform(.008,.063),tint,
                  rng.uniform(.03,.17), .83)

    if not footer:
        # A faint continuation of the storm on the empty end of the tab bar.
        for _ in range(110):
            x,y = rng.uniform(.70,1),rng.uniform(.07,.85)
            light = smooth((x-.69)/.28) * rng.uniform(.16,.44)
            weather = clouds(x, y)
            tint = mix((81,77,52),(190,145,76),smooth((weather-.24)*1.7))
            board.dab(x,y,rng.uniform(.007,.048),rng.uniform(.013,.11),tint,light,.8)
        for x,y in ((.89,.35),(.943,.55),(.966,.24)):
            board.dab(x,y,.0015,.026,(203,167,104),.33,.55)
    return board


if __name__ == "__main__":
    args = ArgumentParser(description=__doc__)
    args.add_argument("output", type=Path)
    args.add_argument("--seed", type=int, default=741)
    args.add_argument("--panel", choices=("sidebar", "header", "footer"), default="sidebar")
    args.add_argument("--width", type=int)
    args.add_argument("--height", type=int)
    options = args.parse_args()
    default_width, default_height = {"sidebar": (384, 1408), "header": (2048, 56),
                                     "footer": (512, 138)}[options.panel]
    width = default_width if options.width is None else options.width
    height = default_height if options.height is None else options.height
    if options.panel == "sidebar":
        board = paint(width, height, options.seed)
    else:
        board = paint_brass(width, height, options.seed, footer=options.panel == "footer")
    board.save(options.output)
