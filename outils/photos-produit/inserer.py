"""Remplace les plans du produit concurrent par les photos du produit de l'élève (recadrage vertical avec zoom lent), à la taille de la vidéo.
Usage : python3 inserer.py <entree.mp4> <sortie.mp4> <reglages.json> [--inserts inserts.json]
reglages.json : {"plans": [
  {"images": [14126, 14340], "photo": "produit/img1.png", "mode": "cadre", "cx": 0.285, "cy": 0.5, "zoom": [1.0, 1.08]},
  {"images": [14341, 14413], "photo": "produit/img4.png", "mode": "carre", "zoom": [1.0, 1.04]},
  {"images": [14591, 14668], "photo": "produit/img1.png", "mode": "cadre", "cx": 0.285, "cy": 0.5, "zoom": [1.0, 1.04], "badge": {"texte": "2+1 OFFERTE", "y": [0.898, 0.964]}}]}
- cadre : morceau vertical de la photo carrée, centré en (cx, cy) (fractions), zoom de zoom[0] à zoom[1] pendant le plan ;
- carre : photo entière au milieu, sur un fond flou de la même photo ; badge : pastille jaune (y en fraction de la hauteur).
Lancer sur la base 1080 (après outils/ia-nettete) pour des photos nettes. Les chemins des photos sont relatifs au fichier de réglages.
--inserts : écrit la liste des plages (pour outils/bandeau-blanc : pas de sous-titre d'origine sur ces images)."""
import sys,os,json,argparse,subprocess,numpy as np
from PIL import Image,ImageDraw,ImageFilter,ImageFont
sys.path.insert(0,'/home/user/amine-monteur-video-ia/amine/scripts')
from common import lire_images,probe,FF
p=argparse.ArgumentParser();p.add_argument('entree');p.add_argument('sortie');p.add_argument('reglages');p.add_argument('--inserts');A=p.parse_args()
C=json.load(open(A.reglages));base=os.path.dirname(os.path.abspath(A.reglages));PR=probe(A.entree);W,H,fps=PR['largeur'],PR['hauteur'],PR['fps']
FONT=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','polices','Poppins-Bold.ttf');cache={}
def photo(f):
    if f not in cache:cache[f]=Image.open(os.path.join(base,f)).convert('RGB')
    return cache[f]
def cadre(img,cx,cy,z):
    S=img.width;h=S/z;w=h*W/H;x0=min(max(cx*S-w/2,0),S-w);y0=min(max(cy*S-h/2,0),S-h);return img.resize((W,H),Image.LANCZOS,box=(x0,y0,x0+w,y0+h))
def carre(img,z):
    fond=cadre(img,0.5,0.5,1.0).filter(ImageFilter.GaussianBlur(W/20));s=int(W*z);fond.paste(img.resize((s,s),Image.LANCZOS),((W-s)//2,(H-s)//2-H//32));return fond
def badge(im,b):
    y0,y1=int(b['y'][0]*H),int(b['y'][1]*H);f=ImageFont.truetype(FONT,int((y1-y0)*0.40));d=ImageDraw.Draw(im);tw=f.getlength(b['texte']);m=(y1-y0)*0.43
    d.rounded_rectangle([W/2-tw/2-m,y0,W/2+tw/2+m,y1],radius=(y1-y0)//2,fill=tuple(b.get('couleur',[251,212,12])));d.text((W/2,(y0+y1)/2+(y1-y0)*0.03),b['texte'],font=f,fill=(26,26,26),anchor='mm');return im
def rend(pl,t):
    z=pl.get('zoom',[1,1]);zz=z[0]+(z[1]-z[0])*t;img=photo(pl['photo'])
    im=cadre(img,pl.get('cx',0.5),pl.get('cy',0.5),zz) if pl.get('mode','cadre')=='cadre' else carre(img,zz)
    return np.asarray(badge(im,pl['badge']) if pl.get('badge') else im,dtype=np.uint8)
wr=subprocess.Popen([FF,'-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(fps),'-i','-','-i',A.entree,'-map','0:v','-map','1:a?','-c:v','libx264','-crf','12','-preset','medium','-pix_fmt','yuv420p','-c:a','copy',A.sortie],stdin=subprocess.PIPE)
for n,im in enumerate(lire_images(A.entree)):
    for pl in C['plans']:
        a,b=pl['images']
        if a<=n<=b:im=rend(pl,(n-a)/max(1,b-a));break
    wr.stdin.write(np.ascontiguousarray(im).tobytes())
wr.stdin.close();wr.wait()
if A.inserts:json.dump([pl['images'] for pl in C['plans']],open(A.inserts,'w'))
print('écrit :',A.sortie)
