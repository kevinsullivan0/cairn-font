"""Long prose and interface specimens for the current Cairn refinement."""
from PIL import Image,ImageDraw,ImageFont

PROSE='''At first light, the keeper opened the archive and found a line of people waiting beneath the broken arch. None had come for the histories of kings. A woman carried a letter folded into a square; a boy held a brass token; an old soldier had brought nothing at all. They wanted names. Beyond the courtyard, the road ran north between low walls of black stone, each block bearing the marks of a different hand.

The keeper set a lamp beside the register. Its pages recorded ordinary things: a bridge repaired, grain delivered, the arrival of rain. Between those entries were the names of people who had not returned. He read slowly, pausing where the ink had faded. “We can keep the record,” he said, “even when we cannot explain it.” The soldier nodded, but the boy continued to watch the open door. Somewhere outside, a cart wheel struck a loose stone, and the sound carried through every empty room.

By 6:40 the square had begun to fill. A mason examined the eastern wall, running one finger along a crack that crossed three names. Repairing it would take a week; replacing it would take a day. He left his tools where they were. The wall had stood through three fires and a winter so bitter that the river froze beneath the bridge. What remained was uneven, awkward, and difficult to mend. It was also the only account anyone trusted.

Before closing the archive that evening, the keeper made one final entry. He wrote the date, counted the letters, and left room for the next name. Outside, the last light rested on the cut faces of the stones. Their edges were still sharp enough to catch a sleeve, though the steps beneath them had worn into shallow bowls. The boy returned the brass token to his pocket. Tomorrow, he would come back with a name.'''

ROWS=[('The northern road','Chapter 03 / Last read at 08:45'),
      ('A record of names','Field notes / Saved yesterday'),
      ('The last watch','Chapter 12 / 24 pages remaining')]


def wrap(text,font,width):
    lines=[];line=''
    for word in text.split():
        proposed=(line+' '+word).strip()
        if line and font.getlength(proposed)>width:lines.append(line);line=word
        else:line=proposed
    if line:lines.append(line)
    return lines


def render_reading_room(fonts,root,labelpath,previous=10,current=11,slug='cairn-iv',heading='CAIRN III / CAIRN IV'):
    paper='#fffcf5';ink='#233033';muted='#78633f';border='#d7d1c3'
    label=ImageFont.truetype(str(labelpath),20);small=ImageFont.truetype(str(labelpath),14)
    indices=[previous,current]
    im=Image.new('RGB',(1500,1250),paper);d=ImageDraw.Draw(im)
    d.text((35,24),heading+' — LONG PROSE',font=label,fill=muted)
    d.text((35,62),'Same nominal 16 px size and 27 px line spacing. Original specimen text.',font=small,fill=muted)
    for col,index in enumerate(indices):
        x=35+col*750;path=str(fonts[index][1]);f=ImageFont.truetype(path,16)
        d.text((x,115),fonts[index][0],font=label,fill=muted)
        d.text((x,165),'Names outlast the walls',font=ImageFont.truetype(path,32),fill=ink)
        y=240
        for paragraph in PROSE.split('\n\n'):
            for line in wrap(paragraph,f,670):
                d.text((x,y),line,font=f,fill=ink);y+=27
            y+=17
        assert y<1035,('Prose exceeds specimen',index,y)
        d.line((x,1050,x+680,1050),fill=border)
        for j,size in enumerate([14,18]):
            yy=1080+j*70
            d.text((x,yy),str(size)+' px',font=small,fill=muted)
            d.text((x+65,yy-3),'After the last watch: rain, stone, memory.',font=ImageFont.truetype(path,size),fill=ink)
    im.save(root/(slug+'-long-prose.png'))

    ui=Image.new('RGB',(1500,1120),'#eeebe3');ud=ImageDraw.Draw(ui)
    ud.text((35,25),heading+' — INTERFACE SPECIMENS',font=label,fill=muted)
    ud.text((35,63),'Body 16 px; secondary labels 14 px; headings 24–28 px. Native raster sizes.',font=small,fill=muted)
    for col,index in enumerate(indices):
        x=35+col*750;path=str(fonts[index][1]);f=ImageFont.truetype(path,16);meta=ImageFont.truetype(path,14)
        ud.text((x,105),fonts[index][0],font=label,fill=muted)
        ud.rounded_rectangle((x,155,x+680,650),radius=8,fill=paper,outline=border)
        ud.text((x+25,175),'Cairn Archive',font=ImageFont.truetype(path,28),fill=ink)
        ud.text((x+25,227),'Library / Field notes / Recent',font=f,fill=muted)
        ud.rounded_rectangle((x+24,279,x+650,327),radius=4,outline=border)
        ud.text((x+40,291),'Search the archive',font=f,fill=muted)
        for j,(title,subtitle) in enumerate(ROWS):
            yy=365+j*91
            ud.text((x+25,yy),title,font=ImageFont.truetype(path,20),fill=ink)
            ud.text((x+25,yy+35),subtitle,font=meta,fill=muted)
            if j<2:ud.line((x+24,yy+72,x+650,yy+72),fill=border)
        ud.rounded_rectangle((x,690,x+680,1080),radius=8,fill=ink)
        ud.text((x+25,713),'Reading preferences',font=ImageFont.truetype(path,24),fill=paper)
        for j,(a,b) in enumerate([('Reading size','16 px'),('Line spacing','1.6'),('Theme','Night'),('Pair spacing','On')]):
            yy=771+j*46
            ud.text((x+25,yy),a,font=f,fill=paper)
            ud.text((x+505,yy),b,font=f,fill=paper)
        for left,right,text in [(25,260,'Save changes'),(290,460,'Return')]:
            ud.rounded_rectangle((x+left,998,x+right,1047),radius=4,outline='#b9b8ab')
            ud.text((x+left+20,1010),text,font=f,fill=paper)
    ui.save(root/(slug+'-interfaces.png'))
