import os,math
from PIL import Image,ImageDraw,ImageFont
OUT="/root/pluginsolarhub/pins"; os.makedirs(OUT,exist_ok=True)
W,H=1000,1500
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"; FR="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
def font(sz,b=True): return ImageFont.truetype(FB if b else FR,sz)
def lerp(a,b,t): return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))
def vgrad(t,b):
 img=Image.new("RGB",(W,H));px=img.load()
 for y in range(H):
  c=lerp(t,b,y/H)
  for x in range(W):px[x,y]=c
 return img
def wrap(d,txt,f,mw):
 ws=txt.split();ls=[];cur=""
 for w in ws:
  t=(cur+" "+w).strip()
  if d.textlength(t,font=f)<=mw:cur=t
  else:ls.append(cur);cur=w
 if cur:ls.append(cur)
 return ls
def sun(d,cx,cy,r,col):
 d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=col)
 for i in range(12):
  a=i*math.pi/6
  d.line([cx+math.cos(a)*(r+16),cy+math.sin(a)*(r+16),cx+math.cos(a)*(r+44),cy+math.sin(a)*(r+44)],fill=col,width=9)
PAL=[((15,32,58),(28,78,140),(245,158,35)),((12,28,52),(20,120,130),(245,180,40)),((38,28,18),(150,90,30),(255,200,60)),((16,40,30),(22,120,80),(250,200,70)),((30,20,45),(90,50,130),(250,170,50)),((20,30,40),(40,90,110),(255,170,45))]
def make(fn,head,sub,cta,pal):
 t,b,ac=pal;img=vgrad(t,b);d=ImageDraw.Draw(img)
 d.rectangle([0,0,W,90],fill=(255,255,255));d.ellipse([40,28,76,64],fill=ac)
 d.text((92,30),"PlugInSolarHub",font=font(34),fill=(20,30,45))
 d.text((W-300,34),"pluginsolarhub.org",font=font(26,False),fill=(120,130,145))
 sun(d,W-150,290,66,ac)
 hf=font(76);y=430
 for ln in wrap(d,head,hf,W-120):d.text((60,y),ln,font=hf,fill=(255,255,255));y+=90
 y+=8;d.rectangle([60,y,250,y+12],fill=ac);y+=46
 sf=font(38,False)
 for ln in wrap(d,sub,sf,W-120):d.text((60,y),ln,font=sf,fill=(225,232,240));y+=52
 d.rectangle([0,H-168,W,H],fill=ac);cf=font(44);tw=d.textlength(cta,font=cf)
 d.text(((W-tw)/2,H-116),cta,font=cf,fill=(255,255,255))
 img.save(f"{OUT}/{fn}",quality=90)
S=[("Alabama","alabama"),("Alaska","alaska"),("Arkansas","arkansas"),("Colorado","colorado"),("Connecticut","connecticut"),("Delaware","delaware"),("Hawaii","hawaii"),("Idaho","idaho"),("Indiana","indiana"),("Iowa","iowa"),("Kansas","kansas"),("Kentucky","kentucky"),("Louisiana","louisiana"),("Maine","maine"),("Maryland","maryland"),("Massachusetts","massachusetts"),("Michigan","michigan"),("Minnesota","minnesota"),("Mississippi","mississippi"),("Missouri","missouri"),("Montana","montana"),("Nebraska","nebraska"),("Nevada","nevada"),("New Hampshire","new-hampshire"),("New Mexico","new-mexico"),("North Dakota","north-dakota"),("Oklahoma","oklahoma"),("Oregon","oregon"),("Rhode Island","rhode-island"),("South Carolina","south-carolina"),("South Dakota","south-dakota"),("Tennessee","tennessee"),("Utah","utah"),("Vermont","vermont"),("Washington","washington"),("West Virginia","west-virginia"),("Wisconsin","wisconsin"),("Wyoming","wyoming")]
H3=["Is Plug-In Solar Legal in {s}? (2026)","Plug-In Solar in {s}: 2026 Rules","Balcony Solar in {s} — What's Allowed?"]
for i,(st,sl) in enumerate(S):
 make(f"state-{sl}.jpg",H3[i%3].format(s=st),f"Balcony & plug-in solar rules, permits and exactly what you can install in {st} — in plain English.","CHECK YOUR STATE'S RULES →",PAL[i%len(PAL)])
print("done",len(S))
