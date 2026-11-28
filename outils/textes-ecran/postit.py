"""Traduit un texte écrit au feutre sur un post-it jaune (suivi image par image, fond refait, main préservée).
Usage : python3 postit.py <entree.mp4> <sortie.mp4> <reglages.json>
reglages.json : {"lignes": ["CARDIOLOGUE –", "APPELER"], "plans": [{"images": [4591, 4696], "zone": [30,150,335,470]},
                 {"images": [12036, 12050], "zone": [165,465,310,610], "effacer_seul": true}], "inclinaison": -3}
- zone : rectangle où chercher le post-it (coordonnées de la vidéo) ; le plus grand morceau jaune est pris, avec les morceaux proches.
- effacer_seul : efface le texte sans en écrire (post-it trop petit ou trop penché pour être réécrit lisiblement).
- Le reste de la vidéo est recopié tel quel (H.264 crf 12, son gardé)."""
import sys,os,json,subprocess,numpy as np
from scipy import ndimage
from scipy.spatial import ConvexHull
from PIL import Image,ImageDraw,ImageFont
sys.path.insert(0,'/home/user/amine-monteur-video-ia/amine/scripts')
from common import lire_images,probe,FF
FONT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','polices','PermanentMarker-Regular.ttf')
def traite(n,im,R_,lignes,incl):
    for pl in R_:
        a,b=pl['images']
        if a<=n<=b:break
    else:return im
    rx0,ry0,rx1,ry1=pl['zone'];A=im.astype(np.float32);R=A[ry0:ry1,rx0:rx1];r,g,bl=R[...,0],R[...,1],R[...,2]
    jaune=(r>165)&(g>135)&(bl<150)&(r-bl>65)&(g-bl>45)
    m=ndimage.binary_closing(jaune,np.ones((7,7)));lab,k=ndimage.label(m)
    if k==0:return im
    tailles=ndimage.sum(m,lab,range(1,k+1));j=int(np.argmax(tailles))+1
    if tailles[j-1]<500:return im
    comp=lab==j;proche=ndimage.binary_dilation(comp,iterations=15)
    for q in range(1,k+1):
        if q!=j and tailles[q-1]>=20 and (proche&(lab==q)).any():comp|=lab==q
    yy,xx=np.where(comp);pts=np.c_[xx,yy];hu=ConvexHull(pts);mk=Image.new('L',(comp.shape[1],comp.shape[0]),0)
    ImageDraw.Draw(mk).polygon([tuple(map(float,pts[v])) for v in hu.vertices],fill=1);note=np.asarray(mk,bool)|ndimage.binary_fill_holes(comp)
    ys,xs=np.where(note);x0,x1,y0,y1=xs.min(),xs.max(),ys.min(),ys.max();w,h=x1-x0,y1-y0
    peau=ndimage.binary_dilation(ndimage.binary_opening((r>150)&(r-g>38)&(g-bl<60)&(bl>80),np.ones((5,5))),iterations=2)  # main (le jaune du papier n'est pas de la peau)
    pin=ndimage.binary_dilation((r>g+50)&(r>bl+50)&(r>80)&~peau,iterations=max(2,int(0.02*np.ptp(xx))))  # aimant rouge
    propre=(jaune&note&~pin&~peau).astype(np.float32);s_=max(3,0.06*w)
    fond=np.stack([ndimage.gaussian_filter(R[...,c]*propre,s_) for c in range(3)],-1)/np.maximum(ndimage.gaussian_filter(propre,s_)[...,None],1e-3)
    zone=note&~peau&~pin&~ndimage.binary_dilation(~note,iterations=2);R[zone]=fond[zone]
    if not pl.get('effacer_seul'):
        tx0,tx1=int(x0+0.04*w),int(x1-0.04*w);ty0,ty1=int(y0+0.22*h),int(y1-0.06*h);cw,ch=tx1-tx0,ty1-ty0
        if cw>10 and ch>8:
            t=max(6,int(ch*0.36));f=ImageFont.truetype(FONT,t)
            while max(f.getlength(l) for l in lignes)>cw*0.92 and t>5:t-=1;f=ImageFont.truetype(FONT,t)
            c=Image.new('L',(cw*3,ch*3),0);dr=ImageDraw.Draw(c);F3=ImageFont.truetype(FONT,t*3);lh=t*3*1.15
            for i,l in enumerate(lignes):dr.text((cw*3/2,ch*3/2+(i-(len(lignes)-1)/2)*lh),l,font=F3,fill=255,anchor='mm')
            c=c.rotate(incl,resample=Image.BICUBIC).resize((cw,ch),Image.LANCZOS);Z=zone[ty0:ty1,tx0:tx1]
            al=(np.asarray(c,np.float32)/255)[...,None]*Z[...,None];R[ty0:ty1,tx0:tx1]=R[ty0:ty1,tx0:tx1]*(1-al)+np.array([40,38,36],np.float32)*al
    out=A.copy();out[ry0:ry1,rx0:rx1]=R;return np.clip(out,0,255).astype(np.uint8)
if __name__=='__main__':
    e,s,cf=sys.argv[1:4];C=json.load(open(cf));P=probe(e);W,H,fps=P['largeur'],P['hauteur'],P['fps']
    wr=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',e,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','12','-preset','medium','-pix_fmt','yuv420p','-c:a','copy',s],stdin=subprocess.PIPE)
    for n,im in enumerate(lire_images(e)):wr.stdin.write(traite(n,im,C['plans'],C['lignes'],C.get('inclinaison',-3)).tobytes())
    wr.stdin.close();wr.wait();print('écrit :',s)
