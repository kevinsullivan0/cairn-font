"""Paint two original daylight banners for Cairn, using the local raster engine."""

from argparse import ArgumentParser
from math import cos, exp, pi, sin, sqrt
from pathlib import Path
from random import Random

from raster import Canvas, Noise, mix, smooth


def ridge(board, samples, bottom, pigment, grain, opacity):
    edge = []
    for left, right in zip(samples, samples[1:]):
        for i in range(8):
            x, y = mix(left, right, i/8)
            edge.append((x, y + .008*(grain(x, y+x*.35)-.5)))
    edge.extend((samples[-1], (samples[-1][0], bottom), (samples[0][0], bottom)))
    board.polygon(edge, pigment, opacity)


def warm_stone(noise, low, high, fall):
    def pigment(x,y):
        seam = noise(x + .14*y, y)
        broken = sin((y - fall*x + .011*seam)*530)
        fleck = noise(x+.146, y+.031)
        tone = smooth(.14 + .43*seam + .18*fleck + .055*broken)
        return mix(low, high, tone)
    return pigment


def soft_bank(points, steps=7):
    """Sample a Catmull–Rom shoreline through the supplied landmarks."""
    extends = [points[0], *points, points[-1]]
    path = []
    for a,b,c,d in zip(extends,extends[1:],extends[2:],extends[3:]):
        for i in range(steps):
            t = i/steps
            path.append(tuple(.5*((2*b[k])+(c[k]-a[k])*t
                                   +(2*a[k]-5*b[k]+4*c[k]-d[k])*t*t
                                   +(-a[k]+3*b[k]-3*c[k]+d[k])*t*t*t)
                              for k in (0,1)))
    return path+[points[-1]]


def crossing(width, height, seed):
    board = Canvas(width, height, samples=4)
    rng = Random(seed)
    sky, weather, grit = (Noise(a,b,seed+i) for i,(a,b) in enumerate(((5,14),(16,35),(48,115))))
    forges = (204, 156, 82)
    shadow = (41, 62, 68)

    def light(x,y):
        daylight = exp(-((x-.63)/.49)**2 - ((y-.35)/.207)**2)
        w = (.72*sky(x+.21*y,y) + .28*weather(x,y))
        cloud = smooth((w-.32)*2.25)
        ground = mix((33,64,79), (105,145,148), daylight*(.63+.21*w))
        return mix(ground, (219,180,117), daylight*.6*cloud)

    board.field(light)
    for _ in range(110):
        x,y = rng.uniform(.09,.99),rng.uniform(.11,.43)
        if weather(x,y) < .54:
            continue
        board.dab(x,y,rng.uniform(.02,.14),rng.uniform(.0016,.0062),
                  (225,191,130),rng.uniform(.06,.18),.68,angle=-6)
    board.dab(.691,.246,.081,.027,(239,193,112),.30)
    board.dab(.691,.246,.024,.024*width/height,(255,228,154),.88,.05)

    ridge(board, [(0,.43),(.10,.409),(.21,.365),(.31,.388),(.393,.365),
                  (.495,.39),(.641,.371),(.779,.356),(.866,.389),(1,.374)],
          .665,(127,135,115),grit,.79)
    ridge(board, [(0,.459),(.088,.416),(.179,.430),(.287,.403),(.432,.452),
                  (.487,.431),(.624,.445),(.755,.403),(.868,.426),(1,.393)],
          .707,(80,109,113),grit,.88)
    ridge(board, [(0,.50),(.125,.484),(.253,.524),(.381,.491),(.46,.556),
                  (.58,.524),(.675,.558),(.78,.509),(.917,.473),(1,.497)],
          1.01,warm_stone(weather,(40,72,74),(76,105,100),-.10),grit,.94)

    # The river catches light in the gap cut by the arch.
    river = [(.53,.546),(.583,.545),(.604,.620),(.529,.672),(.559,.714),
             (.688,.757),(.663,.82),(.475,.876),(.398,.935),(.486,1),
             (.183,1),(.255,.917),(.395,.844),(.538,.801),(.516,.763),
             (.438,.713),(.452,.679),(.557,.624)]
    river = soft_bank(river[:10]) + soft_bank(river[10:])
    board.polygon(river,warm_stone(grit,(52,89,105),(136,158,147),.12),.94)
    with board.clip(river):
        for _ in range(240):
            x,y = rng.uniform(.15,.70),rng.uniform(.55,1)
            tint = mix((137,153,137),(221,182,108),weather(x,y))
            board.dab(x,y,rng.uniform(.007,.055),rng.uniform(.0006,.002),tint,
                      rng.uniform(.09,.45),.77)

    # The deck and single arch, cut as one silhouette so the empty span
    # shows the same terrain and river that continue below it.
    spring, rise, center, half = .577,.109,.548,.247
    def arch(angle, extra=0):
        return center+(half+extra)*cos(angle), spring-(rise+extra*.34)*sin(angle)
    opening = [arch(pi*i/48) for i in range(49)]
    bridge = [(0,.412),(.16,.430),(.34,.430),(.59,.421),(.82,.412),(1,.407),
              (1,.613),(.82,.615),(.795,spring)] + opening
    bridge += [(.255,.611),(.146,.615),(0,.569)]
    shade = warm_stone(grit,(147,102,57),(231,184,106),-.03)
    board.polygon(bridge,shade,1,.06)
    with board.clip(bridge):
        for course in range(15):
            y = .435 + course*.0102
            x = -0.03 if course%2 else -.09
            while x < 1:
                widthstone = rng.uniform(.052,.137)
                xf = x+widthstone
                offset = -.023*(x-.36)
                board.curve((x,y+offset),(x+widthstone*.3,y+offset+.0008),
                            (xf-.017,y+offset-.0007),(xf,y+offset),
                            (88,66,43),.00145,.48,.66)
                board.stroke([(xf,y+offset),(xf-.007,y+offset+.008)],
                             (105,77,44),.0012,.48,.68)
                board.dab(x+widthstone*.4,y+offset-.003,widthstone*.47,.002,
                          forges,.22,.83)
                x = xf

    for i in range(21):
        a,b = pi*i/21,pi*(i+1)/21
        ring = [arch(a),arch((a+b)/2),arch(b),arch(b,.025),
                arch((a+b)/2,.025),arch(a,.025)]
        board.polygon(ring,mix((167,113,58),(245,202,119),rng.uniform(.1,.83)),.91)
        board.stroke([arch(a,.024),arch(a,.005)],(117,86,51),.002,.63,.46)
    board.stroke(opening,(103,76,52),.0025,.63,.5)
    deck = [(0,.416),(.16,.432),(.34,.433),(.59,.424),(.82,.415),(1,.41)]
    board.stroke(deck,(133,94,56),.0068,.91,.44)
    board.stroke([(x,y-.004) for x,y in deck],(247,205,135),.0041,.84,.42)

    left = [(0,.381),(.061,.399),(.143,.417),(.179,.454),(.217,.474),
            (.19,.517),(.231,.575),(.203,.649),(.243,.712),(0,.833)]
    right = [(.918,.426),(.974,.38),(1,.369),(1,.873),(.883,.807),(.805,.731),
             (.825,.66),(.85,.611),(.865,.543),(.847,.496)]
    for bluff in (left,right):
        board.polygon(bluff,warm_stone(grit,(53,61,56),(134,105,69),.22),1,.10)
        with board.clip(bluff):
            for level in range(13):
                start = .417+.029*level
                board.curve((0,start),(.28,start-.032),(.67,start+.07),(1,start+.05),
                            (141,113,75),.0038,.30,.81)
                board.curve((0,start+.004),(.28,start-.027),(.67,start+.074),(1,start+.057),
                            (51,58,48),.0043,.38,.80)
            for _ in range(150):
                x,y=rng.random(),rng.uniform(.39,.86)
                color=mix((54,63,51),(175,129,70),rng.random())
                board.dab(x,y,rng.uniform(.012,.047),rng.uniform(.0006,.004),
                          color,rng.uniform(.09,.48),.82,angle=-22)

    # A small traveler is just enough to give the span its scale.
    board.stroke([(.589,.424),(.592,.414),(.596,.422)],(39,49,46),.003,.94,.27)
    board.dab(.592,.411,.005,.0017,(73,52,42),.9,.31)
    board.stroke([(.588,.416),(.584,.422)],(234,167,83),.0018,.89,.37)
    for x,y in ((.388,.277),(.424,.269),(.46,.278)):
        board.curve((x-.014,y), (x-.008,y-.003),(x-.003,y-.002),(x,y+.001),
                    (72,95,97),.0014,.62)
        board.curve((x,y+.001),(x+.005,y-.002),(x+.009,y-.002),(x+.015,y),
                    (72,95,97),.0014,.62)
    return board


def gardens(width, height, seed):
    board = Canvas(width,height,samples=4)
    rng = Random(seed)
    broad, weather, grain = (Noise(a,b,seed+i+40) for i,(a,b) in enumerate(((4,11),(13,36),(39,102))))

    def dawn(x,y):
        haze=exp(-((x-.72)/.58)**2-((y-.37)/.21)**2)
        clouds=.63*broad(x+.09*y,y)+.37*weather(x,y)
        if y<.48:
            sky=mix((31,75,93),(113,150,148),haze*.86)
            return mix(sky,(230,184,113),haze*smooth((clouds-.30)*2.5)*.53)
        fade=smooth((y-.50)/.52)
        sea=mix((72,133,139),(34,82,89),fade)
        light=exp(-((x-.68)/.39)**2)*(.18-.11*fade)
        return mix(sea,(213,179,111),light*(.7+clouds*.6))

    board.field(dawn)
    for _ in range(138):
        x,y=rng.random(),rng.uniform(.12,.47)
        if weather(x,y)>.54:
            board.dab(x,y,rng.uniform(.022,.16),rng.uniform(.0018,.006),
                      (234,205,155),rng.uniform(.05,.21),.74,angle=-5)
    ridge(board,[(0,.453),(.102,.439),(.188,.455),(.25,.447),(.44,.47),
                 (.58,.463),(.72,.473),(.86,.446),(1,.452)],
          .501,(117,145,129),grain,.77)
    ridge(board,[(0,.474),(.09,.463),(.19,.473),(.32,.483),(.42,.478),(.57,.489),
                 (.74,.476),(.86,.484),(1,.461)],.509,(73,121,125),grain,.72)
    for _ in range(720):
        x,y=rng.random(),rng.uniform(.487,.998)
        w=weather(x,y)
        color=mix((79,151,146),(212,191,129),w*.77)
        board.dab(x,y,rng.uniform(.006,.055),rng.uniform(.0005,.0018),
                  color,rng.uniform(.07,.35),.8)

    island = [(.022,.620),(.124,.602),(.195,.574),(.24,.541),(.309,.531),
              (.381,.479),(.454,.473),(.496,.458),(.573,.461),(.615,.48),
              (.71,.503),(.792,.517),(.874,.519),(1,.526),(1,.819),
              (.86,.811),(.78,.786),(.696,.788),(.599,.758),(.493,.761),
              (.386,.739),(.288,.713),(.215,.717),(.109,.678),(.04,.668)]
    island = soft_bank(island[:14]) + soft_bank(island[14:])
    board.polygon(island,warm_stone(grain,(38,79,67),(103,137,91),.14),1,.06)
    terraces = [
        ((.04,.630),(.218,.608),(.383,.661),(.664,.647),(.852,.639),(1,.655)),
        ((.116,.611),(.26,.578),(.408,.614),(.656,.592),(.852,.585),(1,.603)),
        ((.219,.571),(.36,.527),(.491,.563),(.629,.536),(.833,.542),(1,.558)),
        ((.325,.531),(.435,.481),(.533,.506),(.627,.504),(.753,.524),(1,.539)),
    ]
    greens=((62,113,82),(82,133,82),(120,151,89),(153,168,101))
    for i,(left,control_a,control_b,edge,right,end) in enumerate(terraces):
        boundary = [left]
        for j in range(1,25):
            t=j/24
            u=1-t
            boundary.append(tuple(
                u**3*left[k]+3*u*u*t*control_a[k]+3*u*t*t*control_b[k]+t**3*edge[k]
                for k in (0,1)))
        boundary.extend((right,end))
        beds=boundary+[(x,y+.019+(.012*(1-x))) for x,y in reversed(boundary)]
        board.polygon(beds,warm_stone(grain,greens[i],mix(greens[i],(235,199,113),.41),.05),
                      .96,.12)
        segments = list(zip(boundary,boundary[1:]))
        with board.clip(beds):
            for _ in range(305):
                a,b=rng.choice(segments)
                x,y=mix(a,b,rng.random())
                y+=rng.uniform(.001,.024)
                kind=rng.random()
                tint=(212,166,99) if kind<.14 else (66,106,71) if kind<.49 else (171,189,115)
                board.dab(x,y,rng.uniform(.003,.013),rng.uniform(.0008,.002),
                          tint,rng.uniform(.17,.62),.76,angle=-24+rng.uniform(-11,11))
        surface=(208,173,106) if i in (1,3) else (150,155,104)
        board.stroke(boundary,surface,.0028,.74,.6)
        for j in (4,8,12,15,19,23):
            x,y=boundary[j]
            if (i+j)%4==0:
                continue
            y+=.004
            crown = rng.uniform(.004,.011)
            board.stroke([(x,y+.007),(x+.001,y)],(65,92,66),.0019,.68,.7)
            for _ in range(8):
                board.dab(x+rng.gauss(0,crown*.40),y-.002+rng.gauss(0,.0007),
                          crown,.0025,(99,143,95),rng.uniform(.22,.48),.76,angle=-31)
            board.dab(x-.003,y-.004,crown*.8,.002,(185,180,107),.42,.85)

    # Gates and water channels link the planted terraces down to the tide.
    for a,b,c,d in (
        ((.675,.548),(.732,.583),(.624,.603),(.638,.631)),
        ((.638,.632),(.648,.67),(.51,.661),(.555,.719)),
        ((.555,.719),(.591,.743),(.481,.751),(.473,.803)),
    ):
        board.curve(a,b,c,d,(55,109,112),.0095,.91,.50)
        board.curve(a,b,c,d,(155,204,183),.0032,.61,.61)
        board.dab(*a,.023,.0036,(226,201,131),.37,.61)

    # A sail mill with fabric ribs, above the gravity-fed channels.
    board.polygon([(.471,.472),(.485,.417),(.538,.414),(.565,.474)],
                  warm_stone(grain,(95,96,64),(213,175,106),.04),.98,.08)
    board.polygon([(.466,.424),(.511,.398),(.552,.419),(.551,.426)],
                  (103,86,59),.98)
    board.stroke([(.475,.421),(.511,.398),(.548,.419)],(226,183,109),.003,.69,.54)
    board.polygon([(.506,.471),(.51,.456),(.527,.456),(.532,.47)],(50,81,71),.94)
    cx,cy=.526,.414
    for blade in range(4):
        ang=pi/5+pi*blade/2
        def point(along, across):
            px=along*cos(ang)-across*sin(ang)
            py=along*sin(ang)+across*cos(ang)
            return cx+px,cy+py*width/height
        a,b,c,d=point(.019,-.003),point(.142,-.006),point(.129,.029),point(.050,.021)
        board.polygon([a,b,c,d],warm_stone(grain,(160,144,95),(246,219,151),.10),
                      .94,.10)
        board.stroke([point(0,0),point(.145,0)],(87,93,65),.0033,.92,.5)
        for i in range(1,6):
            u=i/6
            board.stroke([mix(a,b,u),mix(d,c,u)],(135,119,81),.0017,.74,.62)
    board.dab(cx,cy,.012,.012*width/height,(235,190,115),.93,.25)

    # Two workers link the mill and the beds without occupying a UI row.
    for x,y,tint in ((.568,.517,(230,177,105)),(.782,.578,(228,156,107))):
        board.dab(x,y-.008,.0045,.0015,(61,84,62),.95,.3)
        board.stroke([(x,y-.007),(x-.004,y-.003),(x+.006,y)],tint,.004,.87,.35)
        board.stroke([(x,y),(x-.008,y+.004)],(54,84,64),.0023,.76,.4)

    # A hull and its wake leave the lower field with room for labels.
    board.curve((.212,.808),(.28,.834),(.306,.83),(.407,.846),(148,199,172),.0039,.45,.75)
    board.polygon([(.171,.805),(.210,.803),(.245,.799),(.229,.814),(.193,.817)],
                  (64,92,77),.94)
    board.stroke([(.173,.805),(.24,.8)],(231,191,119),.0029,.68,.57)
    board.polygon([(.213,.797),(.208,.768),(.177,.796)],(219,207,153),.81,.16)
    board.stroke([(.213,.801),(.208,.768)],(76,100,76),.0022,.84,.48)
    return board


if __name__ == "__main__":
    args=ArgumentParser(description=__doc__)
    args.add_argument("study",choices=("crossing","gardens"))
    args.add_argument("output",type=Path)
    args.add_argument("--seed",type=int,default=1282)
    args.add_argument("--width",type=int,default=420)
    args.add_argument("--height",type=int,default=1408)
    options=args.parse_args()
    artist={"crossing":crossing,"gardens":gardens}[options.study]
    artist(options.width,options.height,options.seed).save(options.output)
