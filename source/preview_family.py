from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
from reading_room import wrap,PROSE
ROOT=Path(__file__).resolve().parent.parent;LABEL=None
STYLES=['Regular','Italic','Bold','BoldItalic']
INK='#233033';PAPER='#fffcf5';MUTED='#78633f'

def font(style,size):return ImageFont.truetype(str(ROOT/'desktop'/f'Cairn-{style}.ttf'),size)
def label(size=16):return ImageFont.truetype(str(LABEL),size) if LABEL else ImageFont.load_default(size=size)

def render():
    im=Image.new('RGB',(1550,1530),PAPER);d=ImageDraw.Draw(im)
    d.text((45,30),'CAIRN / FIRST EDITION',font=label(23),fill=MUTED)
    d.text((45,90),'What the stone remembers',font=font('Regular',75),fill=INK)
    for i,style in enumerate(STYLES):
        y=220+i*300
        d.text((45,y),style.replace('BoldItalic','Bold Italic'),font=label(18),fill=MUTED)
        d.text((45,y+38),'abcdefghijklmnopqrstuvwxyz',font=font(style,48),fill=INK)
        d.text((45,y+110),'ABCDEFGHIJKLMNOPQRSTUVWXYZ',font=font(style,40),fill=INK)
        d.text((45,y+175),'0123456789   Il1 O0 rn m   “Words”—and names…',font=font(style,34),fill=INK)
        d.text((45,y+239),'At the broken gate, a keeper waits for the last name.',font=font(style,18),fill=INK)
    im.save(ROOT/'proofs/family.png')
    im=Image.new('RGB',(1500,1410),PAPER);d=ImageDraw.Draw(im)
    d.text((35,25),'CAIRN / SMALL TYPE, FOUR STYLES',font=label(21),fill=MUTED)
    for i,style in enumerate(STYLES):
        y=90+i*320
        d.text((35,y),style,font=label(18),fill=MUTED)
        for j,size in enumerate([12,14,16,18,20]):
            yy=y+45+j*43
            d.text((35,yy),str(size)+' px',font=label(12),fill=MUTED)
            d.text((105,yy-3),'The quiet keeper reads the names. minimum rn m Il1 O0 aeog ij ft.',font=font(style,size),fill=INK)
        d.rectangle((25,y+264,1475,y+310),fill=INK)
        d.text((105,y+275),'Return to the archive • 08:45',font=font(style,16),fill=PAPER)
    im.save(ROOT/'proofs/small-text.png')
    im=Image.new('RGB',(1500,1280),'#eeebe3');d=ImageDraw.Draw(im)
    d.text((35,25),'CAIRN / PROSE AND INTERFACE',font=label(21),fill=MUTED)
    d.rectangle((25,90,740,1240),fill=PAPER)
    d.text((50,115),'Names outlast the walls',font=font('Bold',33),fill=INK)
    d.text((50,172),'A record of the last watch',font=font('Italic',20),fill=MUTED)
    y=225
    for para in PROSE.split('\n\n'):
        for line in wrap(para,font('Regular',18),650):
            d.text((50,y),line,font=font('Regular',18),fill=INK);y+=30
        y+=20
    assert y<1230,y
    x=790;d.rectangle((765,90,1475,625),fill=PAPER)
    d.text((x,120),'The Archive',font=font('Bold',35),fill=INK)
    d.text((x,180),'Library / Field notes / Recent',font=font('Regular',16),fill=MUTED)
    for j,(title,subtitle) in enumerate([('The northern road','Chapter 03 / Last read at 08:45'),('A record of names','Field notes / Saved yesterday'),('The last watch','Chapter 12 / 24 pages remaining')]):
        yy=250+j*110
        d.text((x,yy),title,font=font('Bold',21),fill=INK)
        d.text((x,yy+39),subtitle,font=font('Regular',14),fill=MUTED)
        d.line((x,yy+83,1445,yy+83),fill='#ddd6c8')
    d.rectangle((765,655,1475,1240),fill=INK)
    d.text((x,690),'The last entry',font=font('BoldItalic',35),fill=PAPER)
    quote='“We can keep the record,” he said, “even when we cannot explain it.”'
    y=775
    for line in wrap(quote,font('Italic',24),620):
        d.text((x,y),line,font=font('Italic',24),fill=PAPER);y+=39
    d.text((x,1020),'Reading size',font=font('Regular',16),fill=PAPER)
    d.text((1320,1020),'18 px',font=font('Bold',16),fill=PAPER)
    d.text((x,1080),'Line spacing',font=font('Regular',16),fill=PAPER)
    d.text((1320,1080),'1.65',font=font('Bold',16),fill=PAPER)
    d.rectangle((x,1145,x+210,1200),outline='#aaa996')
    d.text((x+22,1160),'Save changes',font=font('Bold',18),fill=PAPER)
    im.save(ROOT/'proofs/prose-interface.png')

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('root',type=Path,nargs='?',default=ROOT);p.add_argument('--label',type=Path)
    a=p.parse_args();ROOT=a.root;LABEL=a.label;render()
